from typing import List, Optional

from rest_framework.response import Response
from rest_framework import status, generics
from applications.models import JobApplication
from applications_api.serializers import JobApplicationSerializer
from datetime import date


class JobApplications(generics.GenericAPIView):
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()

    def get_sort(self, request) -> Optional[List[str]]:
        """
        Parse the request to get the ordering information and return it in a Django compliant list.
        The method returns None if there is no sorting requested.

        :param request:
        :return:
        """
        sort_order = []
        i = 0
        name = request.GET.get("order[%i][name]" % i)
        while name is not None:
            direction = request.GET.get("order[%i][dir]" % i)
            if direction == 'desc':
                sort_order.append('-' + name)
            else:
                sort_order.append(name)
            i += 1
            name = request.GET.get("order[%i][name]" % i)

        if len(sort_order) == 0:
            sort_order = None

        return sort_order

    def get(self, request):
        draw = int(request.GET.get("draw", 1))
        start_num = int(request.GET.get("start", 1))
        length = int(request.GET.get("length", 10))
        end_num = start_num + length
        search_param = request.GET.get("search[value]")
        job_applications = JobApplication.objects.all()
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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['when'] = date.today()
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "job_application": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "status": "fail",
                    "message": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class JobApplicationDetail(generics.GenericAPIView):
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()

    def get_application(self, pk):
        try:
            return JobApplication.objects.get(pk=pk)
        except Exception:
            return None

    def get(self, request, pk):
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

    def patch(self, request, pk):
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
        else:
            return Response(
                {
                    "status": "fail",
                    "message": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
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
