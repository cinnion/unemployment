"""
Tests for JobApplicationScraper
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from playwright.sync_api import TimeoutError, Error  # pylint: disable=redefined-builtin

from applications_api.views import JobApplicationScraper


class TestApplicationScraper(APITestCase):
    """
    Tests for the job applications scraper API.
    """

    api_url = "applications-api:applications-scraper"

    @classmethod
    def setUpClass(cls):
        """
        Set up our common test_url.
        """
        super().setUpClass()
        cls.test_url = reverse("applications-api:applications-list")

    def test_clean_query_one_param_gets_expected_query_string_back(self):
        # Arrange
        qs = "utm_source=jobalert&utm_medium=email&jl=1010184134072&utm_content=ja-jobpos12-age1d-1010184134072&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=44191B1DF3FAD251A1E228DD5DF01DEE&ao=1136043&jrtk=5-yul1-0-1jsg5bnh0h71s800-d44b3eba31c3a796&cs=1_91561ef8&s=224&t=JA&pos=112&ja=409415552&guid=0000019f1ffc145e86377cd98d613ca9&jobListingId=1010184134072&ea=1&vt=e&cb=1782953926400&ctt=1783722907050&srs=EMAIL_JOB_ALERT&gdir=1"  # pylint: disable=line-too-long
        wanted_params = ["jl"]
        expected = "jl=1010184134072"
        instance = JobApplicationScraper()

        # Act
        results = instance.clean_query(qs, wanted_params)

        # Assert
        self.assertEqual(results, expected)

    def test_clean_query_two_params_gets_expected_query_string_back(self):
        # Arrange
        qs = "utm_source=jobalert&utm_medium=email&jl=1010184134072&utm_content=ja-jobpos12-age1d-1010184134072&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=44191B1DF3FAD251A1E228DD5DF01DEE&ao=1136043&jrtk=5-yul1-0-1jsg5bnh0h71s800-d44b3eba31c3a796&cs=1_91561ef8&s=224&t=JA&pos=112&ja=409415552&guid=0000019f1ffc145e86377cd98d613ca9&jobListingId=1010184134072&ea=1&vt=e&cb=1782953926400&ctt=1783722907050&srs=EMAIL_JOB_ALERT&gdir=1"  # pylint: disable=line-too-long
        wanted_params = ["jl", "utm_medium"]
        expected = "utm_medium=email&jl=1010184134072"
        instance = JobApplicationScraper()

        # Act
        results = instance.clean_query(qs, wanted_params)

        # Assert
        self.assertEqual(results, expected)

    def test_save_post_by_id_file_with_correct_contents(self):
        # Arrange
        contents = "Some contents"
        post_id = 9999
        instance = JobApplicationScraper()
        file_path = Path("applications_api/tests/fixtures/009999.html")
        self.assertFalse(file_path.exists())

        # Act
        instance.save_post_by_id(post_id, contents)

        # Assert
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            results = f.read()
        self.assertEqual(results, contents)
        file_path.unlink()

    def setup_playwright_mocking(self, mock_sync_playwright):
        """
        Arrange the set of playwright calls

        Args:
            mock_sync_playwright: The mock for the sync_playwright context
                generator.

        Returns:
            A tuple consisting of the mock playwright, mock browser, mock
        browser context, mock_page and mock response.

        """
        # Arrange the main sync_playwright() context
        mock_p = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_p

        # Now arrange the connect_over_cdp() call, along with the
        mock_browser = MagicMock()
        mock_p.chromium.connect_over_cdp.return_value = mock_browser

        # Next, arrange the calls for the new_context() call.
        mock_context = MagicMock()
        mock_browser.new_context.return_value = mock_context

        # And the new_page() call.
        mock_page = MagicMock()
        mock_context.new_page.return_value = mock_page

        # And the goto() call.
        mock_response = MagicMock()
        mock_page.goto.return_value = mock_response

        return mock_p, mock_browser, mock_context, mock_page, mock_response

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_no_errors_returns_results(self, mock_sync_playwright):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        expected_content = "<html>Mocked Content<html>"
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        mock_page.content.return_value = expected_content
        mock_response.status = 200
        mock_response.status_text = ""

        # Act
        with self.assertLogs("applications_api.views", level="DEBUG") as captured:
            resulting_status, resulting_text, resulting_contents = instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(
            captured.output,
            ["DEBUG:applications_api.views:Sending obscura request to target URL: https://target.example.com"],
        )
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_called_once_with()
        mock_context.new_page.assert_called_once_with()
        mock_page.goto.assert_called_once_with(target_url, wait_until="networkidle")
        mock_context.close.assert_called_once_with()
        mock_browser.close.assert_called_once_with()

        self.assertEqual(resulting_status, 200)
        self.assertEqual(resulting_text, "")
        self.assertEqual(resulting_contents, expected_content)

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_connection_timesout_expected_log_message_and_exception_raised(
        self, mock_sync_playwright
    ):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, _mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        orig_exception = TimeoutError("A timeout message")
        mock_p.chromium.connect_over_cdp.side_effect = orig_exception

        # Act
        with (
            self.assertLogs("applications_api.views", level="DEBUG") as captured,
            self.assertRaisesRegex(RuntimeError, rf"Error getting posting from {target_url}") as ce,
        ):
            instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(captured.output, ["ERROR:applications_api.views:The connection failed: A timeout message"])
        self.assertIsNotNone(ce.exception.__cause__)
        self.assertIsInstance(ce.exception.__cause__, TimeoutError)
        self.assertEqual(str(ce.exception.__cause__), "A timeout message")
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_not_called()
        mock_context.new_page.assert_not_called()
        mock_page.goto.assert_not_called()

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_new_context_fails_expected_log_message_and_exception_raised(
        self, mock_sync_playwright
    ):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, _mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        orig_exception = TimeoutError("Some new_context error")
        mock_browser.new_context.side_effect = orig_exception

        # Act
        with (
            self.assertLogs("applications_api.views", level="DEBUG") as captured,
            self.assertRaisesRegex(RuntimeError, rf"Error getting posting from {target_url}") as ce,
        ):
            instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(
            captured.output, ["ERROR:applications_api.views:Error getting new browser context: Some new_context error"]
        )
        self.assertIsNotNone(ce.exception.__cause__)
        self.assertIsInstance(ce.exception.__cause__, TimeoutError)
        self.assertEqual(str(ce.exception.__cause__), "Some new_context error")
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_called_once_with()
        mock_context.new_page.assert_not_called()
        mock_page.goto.assert_not_called()
        mock_browser.close.assert_called_once_with()
        mock_context.close.assert_not_called()

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_new_page_fails_expected_log_message_and_exception_raised(
        self, mock_sync_playwright
    ):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, _mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        orig_exception = TimeoutError("Some new_page error")
        mock_context.new_page.side_effect = orig_exception

        # Act
        with (
            self.assertLogs("applications_api.views", level="DEBUG") as captured,
            self.assertRaisesRegex(RuntimeError, rf"Error getting posting from {target_url}") as ce,
        ):
            instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(captured.output, ["ERROR:applications_api.views:Error getting new page: Some new_page error"])
        self.assertIsNotNone(ce.exception.__cause__)
        self.assertIsInstance(ce.exception.__cause__, TimeoutError)
        self.assertEqual(str(ce.exception.__cause__), "Some new_page error")
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_called_once_with()
        mock_context.new_page.assert_called_once_with()
        mock_page.goto.assert_not_called()
        # mock_browser.close.assert_called_once_with()
        mock_context.close.assert_called_once_with()

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_goto_timeout_expected_log_message_and_exception_raised(
        self, mock_sync_playwright
    ):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, _mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        orig_exception = TimeoutError("Some goto timeout")
        mock_page.goto.side_effect = orig_exception

        # Act
        with (
            self.assertLogs("applications_api.views", level="DEBUG") as captured,
            self.assertRaisesRegex(RuntimeError, rf"Timeout error getting page: {orig_exception}") as ce,
        ):
            instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(
            captured.output,
            [
                "DEBUG:applications_api.views:Sending obscura request to target URL: https://target.example.com",
                "ERROR:applications_api.views:The page operation timed out! Some goto timeout",
            ],
        )
        self.assertIsNotNone(ce.exception.__cause__)
        self.assertIsInstance(ce.exception.__cause__, TimeoutError)
        self.assertEqual(str(ce.exception.__cause__), "Some goto timeout")
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_called_once_with()
        mock_context.new_page.assert_called_once_with()
        mock_page.goto.assert_called_once_with(target_url, wait_until="networkidle")
        mock_context.close.assert_called_once_with()
        mock_browser.close.assert_called_once_with()

    @patch("applications_api.views.sync_playwright")
    def test_get_posting_with_obscura_goto_error_expected_log_message_and_exception_raised(self, mock_sync_playwright):
        # Arrange the instance and sync_playwright context.
        instance = JobApplicationScraper()
        mock_p, mock_browser, mock_context, mock_page, _mock_response = self.setup_playwright_mocking(
            mock_sync_playwright
        )
        target_url = "https://target.example.com"
        cdp_uri = settings.OBSCURA_SERVER_CDP_URL

        # Arrange the returned page and the response.
        orig_exception = Error("Some goto error")
        mock_page.goto.side_effect = orig_exception

        # Act
        with (
            self.assertLogs("applications_api.views", level="DEBUG") as captured,
            self.assertRaisesRegex(RuntimeError, rf"Playwright error getting page: {orig_exception}") as ce,
        ):
            instance.get_posting_with_obscura(target_url)

        # Assert
        self.assertEqual(
            captured.output,
            [
                "DEBUG:applications_api.views:Sending obscura request to target URL: https://target.example.com",
                "ERROR:applications_api.views:A general Playwright error occurred: Some goto error",
            ],
        )
        self.assertIsNotNone(ce.exception.__cause__)
        self.assertIsInstance(ce.exception.__cause__, Error)
        self.assertEqual(str(ce.exception.__cause__), "Some goto error")
        mock_p.chromium.connect_over_cdp.assert_called_once_with(cdp_uri)
        mock_browser.new_context.assert_called_once_with()
        mock_context.new_page.assert_called_once_with()
        mock_page.goto.assert_called_once_with(target_url, wait_until="networkidle")
        mock_context.close.assert_called_once_with()
        mock_browser.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
