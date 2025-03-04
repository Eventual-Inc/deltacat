from unittest.mock import patch
import unittest
from http import HTTPStatus
import requests

HAPPY_RESPONSE = {
    "AccessKeyId": "ASIA123456789",
    "Code": "Success",
    "Expiration": "2023-08-02T13:50:33Z",
    "LastUpdated": "2023-08-02T07:23:35Z",
    "SecretAccessKey": "bar",
    "Token": "foo",
    "Type": "AWS-HMAC",
}


class MockResponse:
    """
    A mock object denoting the response of requests method.
    """

    def __init__(self, status_code: int, text: str, reason: str = "") -> None:
        self.status_code: requests.Response.status_code = status_code
        self.text = text
        self.reason = reason

    def raise_for_status(*args, **kwargs):
        pass


class TestBlockUntilInstanceMetadataServiceReturnsSuccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    @patch("deltacat.aws.clients.requests")
    def test_sanity(self, requests_mock):
        from deltacat.aws.clients import (
            block_until_instance_metadata_service_returns_success,
        )

        requests_mock.get.return_value = MockResponse(200, "foo")
        self.assertEqual(
            block_until_instance_metadata_service_returns_success().status_code, 200
        )

    @patch("deltacat.aws.clients.requests")
    def test_retrying_on_statuses_in_status_force_list(self, requests_mock):
        from deltacat.aws.clients import (
            block_until_instance_metadata_service_returns_success,
        )

        requests_mock.get.side_effect = [
            MockResponse(HTTPStatus.OK, "foo"),
            MockResponse(HTTPStatus.TOO_MANY_REQUESTS, "foo"),
            MockResponse(HTTPStatus.INTERNAL_SERVER_ERROR, "foo"),
            MockResponse(HTTPStatus.NOT_IMPLEMENTED, "bar"),
            MockResponse(HTTPStatus.SERVICE_UNAVAILABLE, "bar"),
            MockResponse(HTTPStatus.GATEWAY_TIMEOUT, "bar"),
        ]
        self.assertEqual(
            block_until_instance_metadata_service_returns_success().status_code, 200
        )

    @patch("deltacat.aws.clients.requests")
    def test_retrying_status_on_shortlist_returns_early(self, requests_mock):
        from deltacat.aws.clients import (
            block_until_instance_metadata_service_returns_success,
        )

        requests_mock.get.side_effect = [
            MockResponse(HTTPStatus.FORBIDDEN, "foo"),
        ]
        self.assertEqual(
            block_until_instance_metadata_service_returns_success().status_code, 403
        )
