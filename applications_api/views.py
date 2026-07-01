"""
Views for the DRF API for job applications.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlsplit, SplitResult, parse_qs, urlencode

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models.query import QuerySet
from django.forms import model_to_dict
from playwright.sync_api import TimeoutError, sync_playwright, Error  # pylint: disable=redefined-builtin
from requests import HTTPError
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import JobApplication, JobPost
from applications_api.serializers import JobApplicationSerializer

logger = logging.getLogger(__name__)


class JobApplications(GenericAPIView):
    """
    The view for job applications presented through the DRF API.
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self) -> QuerySet:
        """
        This view will return a QuerySet of all the applications made by the currently authenticated user.
        """
        user_id = self.request.user.id
        return JobApplication.objects.filter(user_id=user_id)

    @staticmethod
    def get_sort(request: Request) -> Optional[List[str]]:
        """
        Parse the request to get the ordering information and return it in a Django compliant list.
        The method returns None if there is no sorting requested.

        :param request:
        :return:
        """
        sort_order = []
        i = 0
        name = request.GET.get(f"order[{i}][name]")
        while name is not None:
            direction = request.GET.get(f"order[{i}][dir]")
            if direction == "desc":
                sort_order.append("-" + name)
            else:
                sort_order.append(name)
            i += 1
            name = request.GET.get(f"order[{i}][name]")

        if len(sort_order) == 0:
            sort_order = None

        return sort_order

    def get(self, request: Request) -> Response:
        """
        Our GET request handler for the API.

        Args:
            request (Request): The API request.

        Returns:

        """
        draw = int(request.GET.get("draw", 1))
        start_num = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        end_num = start_num + length
        search_param = request.GET.get("search[value]")
        job_applications = self.get_queryset()
        total_applications = job_applications.count()
        total_filtered = total_applications
        sort_order = self.get_sort(request)

        if search_param:
            job_applications = job_applications.filter(company__icontains=search_param)
            total_filtered = job_applications.count()

        if sort_order:
            job_applications = job_applications.order_by(*sort_order)

        serializer = self.serializer_class(job_applications[start_num:end_num], many=True)

        return Response(
            {
                "status": "success",
                "draw": draw,
                "recordsTotal": total_applications,
                "recordsFiltered": total_filtered,
                "job_applications": serializer.data,
            }
        )

    def post(self, request: Request) -> Response:  # pragma: no cover
        """
        This method is currently not used, and is blocked from being run by the http_method_names property.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data["when"] = date.today()
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "job_application": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "fail",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class JobApplicationDetail(GenericAPIView):  # pragma: no cover
    """
    This class is currently not used
    """

    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_application(pk: int) -> JobApplication | None:
        """
        A common method to get a job application by its primary key.

        Args:
            pk (int): The primary key

        Returns:
            A Response object containing the job application.

        """
        # noinspection PyBroadException
        try:
            return JobApplication.objects.get(pk=pk)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get(self, request: Request, pk: int) -> Response:
        """
        HTTP get handler to get a job application.

        Args:
            request (Request): Our request
            pk (int): The primary key

        Returns:
            The response object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(job_application)
        return Response(
            {
                "status": "success",
                "job_application": serializer.data,
            }
        )

    def patch(self, request: Request, pk: int) -> Response:
        """
        The HTTP PATCH request handler.

        Args:
            request (Request): The request object.
            pk (int): The primary key.

        Returns:
            The response object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "job_application": serializer.data,
                },
            )

        return Response(
            {
                "status": "fail",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request: Request, pk: int) -> Response:
        """
        The HTTP delete method handler.

        Args:
            request (Request): The request object.
            pk (int): The primary key.

        Returns:
            The response object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        job_application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobApplicationScraper(APIView):
    """
    A class for cleaning up a job post URL.
    """

    handlers = {
        "www.dice.com": "handle_dice_url",
        "www.glassdoor.com": "handle_glassdoor_url",
        "www.greenhouse.com": "handle_greenhouse_url",
        "www.indeed.com": "handle_indeed_url",
        "www.linkedin.com": "handle_linkedin_url",
        "www.ziprecruiter.com": "handle_ziprecruiter_url",
    }

    @staticmethod
    def clean_query(query: str, wanted_params: list[str]) -> str:
        """
        Clean unwanted parameters from a query string.

        Args:
            query: The initial query string.
            wanted_params: A list of parameters which we want.

        Returns:
            The cleaned up query string.
        """
        query = parse_qs(query)

        for key, _value in dict(query):
            if key not in wanted_params:
                del query[key]

        return urlencode(query, doseq=True)

    @staticmethod
    def save_post_by_id(post_id: int, contents: str) -> None:
        """
        Save the contents in a file.

        Args:
            post_id: The ID from the database
            contents: The contents

        Returns: None
        """
        module_dir = Path(__file__).resolve().parent
        file_path = module_dir / "tests/fixtures" / f"{post_id:06d}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(contents)

    @staticmethod
    def get_posting(url: SplitResult) -> tuple[int, str]:
        """
        Get the page associated with the url, and save it to disk.

        Args:
            url: The split URL.

        Returns:
            The HTML for the main page of the job post.
        """
        response = requests.get(url.geturl(), timeout=10)

        if response.status_code == 200:
            module_dir = Path(__file__).resolve().parent
            file_path = module_dir / "tests/fixtures" / (url.hostname + ".html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        else:
            logger.warning("Site %s returned a non-200 return code", response.status_code)
            response.raise_for_status()

        return int(response.status_code), response.text

    @staticmethod
    def get_posting_with_obscura(target_url: str) -> tuple[int, str, str]:
        """
        Use our obscura service to request a job posting page.

        Args:
            target_url: The cleaned up URL.

        Returns:
            The status, status text, and page contents.
        """
        obscura_cdp_url: str = settings.OBSCURA_SERVER_CDP_URL

        with sync_playwright() as p:
            # Connect to obscura
            browser = p.chromium.connect_over_cdp(obscura_cdp_url)

            # Open a fresh isolated context and page
            context = browser.new_context()
            page = context.new_page()

            # Set a default status and content
            http_status = -1
            status_text = ""
            html_content = ""

            # Now try to get the page.
            try:
                # Send the request.
                logger.debug("Sending obscura request to target URL: %s", target_url)
                response = page.goto(target_url, wait_until="networkidle")

                # Get the content
                html_content = page.content()
                http_status = response.status
                status_text = response.status_text
            except TimeoutError:
                logger.error("The page operation timed out!")
            except Error as e:
                logger.error("A general Playwright error occurred: %s", e)
            finally:
                # Cleanup the session context
                context.close()
                browser.close()

            return http_status, status_text, html_content

    def handle_dice_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean a Dice URL.

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """

        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        company = ""
        title = ""

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company,
            "title": title,
        }

    def handle_glassdoor_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean an Indeed URL, which consists of the following:
            - scheme
            - netloc
            - path
            - query (just jl)
            (fragment is dropped)

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """

        # Clean the query string and replace it and fragment in the URL.
        query = self.clean_query(url.query, ["jl"])
        url = url._replace(query=query, fragment="")

        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        company = ""
        title = ""

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company,
            "title": title,
        }

    def handle_greenhouse_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean a Greenhouse URL.

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """

        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        company = ""
        title = ""

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company,
            "title": title,
        }

    def handle_indeed_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean an Indeed URL.

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """

        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        company = ""
        title = ""

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company,
            "title": title,
        }

    def handle_linkedin_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean a LinkedIn URL.

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """

        # Cleanup our known patterns of URLs from linkedin.
        if url.path == "/jobs/collections/recommended/":
            qs = parse_qs(url.query)
            url = url._replace(path=f"/jobs/view/{qs['currentJobId'][0]}/", query="")
        elif url.path.startswith("/jobs/view/"):
            url = url._replace(query="")
        else:
            logger.warning("Unrecognized URL format for linkedin.com: %s", url.geturl())
            raise ValueError(f"Unrecognized URL format for linkedin.com: {url.geturl()}")

        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        if http_status == 200:
            soup = BeautifulSoup(contents, "html.parser")

            title = soup.find("h1", class_="top-card-layout__title").get_text().strip()
            company = soup.find("a", class_="topcard__org-name-link").get_text().strip()
            description = soup.find("div", class_="description__text").get_text()

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company if company else "",  # pylint: disable=possibly-used-before-assignment
            "title": title if title else "",  # pylint: disable=possibly-used-before-assignment
            "description": description if description else "",  # pylint: disable=possibly-used-before-assignment
        }

    def handle_ziprecruiter_url(self, url: SplitResult) -> dict[str, str | int]:
        """
        Clean a ZipRecruiter URL.

        Args:
            url: The split URL

        Returns:
            A dictionary consisting of the following
                - clean_url: The clean url
                - http_status: The http status returned when we requested the page.
                - status_text: The http status text returned when we requested the page.
                - contents: The page contents.
                - company: The posting company, or blank if we did not find it.
                - title: The posted job title, or blank if we did not find it.

        Raises:
            ValueError if the exact pattern is not recognized.
        """
        # Get the job post.
        url = url.geturl()
        http_status, status_text, contents = self.get_posting_with_obscura(url)

        # TODO - Parse the contents to get the company and title.
        company = ""
        title = ""

        # Return the results.
        return {
            "clean_url": url,
            "http_status": http_status,
            "status_text": status_text,
            "contents": contents,
            "company": company,
            "title": title,
        }

    def clean_unknown_url(self, url: SplitResult) -> tuple[SplitResult, int, str]:
        """
        Handle unrecognized host names.

        Args:
            url: The split URL

        Returns:
            A clean URL?

        Raises:
            ValueError if we do not recognize the URL.
        """
        json_url = json.dumps(url)
        logger.warning('Unrecognised host URL: host="%s", url=%s', url.hostname, json_url)
        raise ValueError("Unrecognized host {url.hostname}")

    def post(self, request: Request) -> Response:
        """
        Take a request containing a URL and clean it up for later storing.

        Args:
            request: The request object.

        Returns:
            A response containing the clean URL.
        """
        raw_url = None
        if "url" in request.data:
            raw_url = request.data["url"]

        # If passed the raw URL...
        if raw_url:
            try:
                # See if we have looked it up before...
                if JobPost.objects.filter(raw_url=raw_url).exists():

                    # We have...use those results...
                    post_details = JobPost.objects.filter(raw_url=raw_url).get()
                    posting_id = post_details.id
                    post_details = model_to_dict(post_details)
                else:

                    # Gotta go fetch it. Start by splitting the raw URL, which
                    # we will proceed to cleanup.
                    url = urlsplit(raw_url)
                    if url.hostname in self.handlers:
                        func = getattr(self, self.handlers[url.hostname])
                        post_details = func(url)

                        job_post, created = JobPost.objects.get_or_create(raw_url=raw_url, defaults={**post_details})
                        posting_id = job_post.id
                        if created:
                            self.save_post_by_id(posting_id, post_details["contents"])
                    else:
                        json_url = json.dumps(url)
                        logger.warning('Unrecognised host URL: host="%s", url=%s', url.hostname, json_url)
                        raise NotImplementedError("Handler for host {url.hostname} not implemented")

            except (NotImplementedError, ValueError, HTTPError) as e:
                data = {"error": str(e)}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:  # pylint: disable=broad-exception-caught
                data = {"error": str(e)}
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data = {
                "clean_url": post_details["clean_url"],
                "post_status": post_details["http_status"],
                "status_text": post_details["status_text"],
                "company": post_details["company"],
                "title": post_details["title"],
                "posting_id": posting_id,
            }
            return Response(data)

        data = {"error": "Unable to parse URL"}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
