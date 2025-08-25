"""Tests for API Client"""

import pytest
import requests
from unittest.mock import Mock, patch
from src.lib.api import ApiClient


@pytest.fixture
def client():
    """Fixture for ApiClient with base URL and timeout."""
    return ApiClient(base_url="https://api.example.com", timeout=10)


@pytest.fixture
def mock_response():
    """Factory fixture to create a mock response object."""
    def _create(status_code=200, text="OK", json_data=None):
        response = Mock()
        response.status_code = status_code
        response.text = text
        response.json.return_value = json_data or {}
        return response
    return _create


class TestApiClient:
    """Test suite for API Client."""

    def test_initialization_with_defaults(self):
        client = ApiClient()
        assert client.base_url == ""
        assert client.default_headers == {}
        assert client.timeout == 30

    def test_initialization_with_custom_values(self):
        headers = {"Authorization": "Bearer token"}
        client = ApiClient(
            base_url="https://custom.api.com/", default_headers=headers, timeout=60
        )
        assert client.base_url == "https://custom.api.com"
        assert client.default_headers == headers
        assert client.timeout == 60

    def test_build_url_with_and_without_base(self, client):
        assert client._build_url("/endpoint") == "https://api.example.com/endpoint"
        assert client._build_url("endpoint") == "https://api.example.com/endpoint"
        assert ApiClient()._build_url("https://full.url.com/x") == "https://full.url.com/x"

    def test_set_headers_and_auth(self, client):
        headers = {"Content-Type": "application/json"}
        client.set_default_headers(headers)
        assert client.default_headers == headers

        client.set_auth_header("test_token", "Bearer")
        assert client.default_headers["Authorization"] == "Bearer test_token"

        client.set_auth_header("test_key", "ApiKey")
        assert client.default_headers["Authorization"] == "ApiKey test_key"

        client.set_auth_header("custom_value", "Custom")
        assert client.default_headers["Authorization"] == "Custom custom_value"

    def test_successful_get_request(self, client, mock_response):
        response = mock_response(200, "Success", {"status": "ok"})
        with patch("requests.get", return_value=response) as mock_get, patch(
            "src.lib.api.api_logger"
        ) as mock_logger:
            result = client.get("/test")

            assert result == response
            mock_get.assert_called_once_with(
                "https://api.example.com/test", headers={}, params=None, timeout=10
            )
            mock_logger.log_successful_call.assert_called_once()

    def test_get_request_with_params_and_headers(self, client, mock_response):
        response = mock_response(200)
        with patch("requests.get", return_value=response) as mock_get, patch(
            "src.lib.api.api_logger"
        ):
            params = {"key": "value"}
            headers = {"Custom-Header": "custom-value"}
            client.get("/test", params=params, headers=headers)

            expected_headers = {**client.default_headers, **headers}
            mock_get.assert_called_once_with(
                "https://api.example.com/test",
                headers=expected_headers,
                params=params,
                timeout=10,
            )

    def test_successful_post_request(self, client, mock_response):
        response = mock_response(200, "Created")
        with patch("requests.post", return_value=response) as mock_post, patch(
            "src.lib.api.api_logger"
        ) as mock_logger:
            result = client.post("/create", data={"x": 1})
            assert result == response
            mock_post.assert_called_once()
            mock_logger.log_successful_call.assert_called_once()

    def test_post_request_with_headers(self, client, mock_response):
        response = mock_response(200)
        with patch("requests.post", return_value=response) as mock_post, patch(
            "src.lib.api.api_logger"
        ):
            headers = {"Content-Type": "application/json"}
            client.post("/test", data={}, headers=headers)

            expected_headers = {**client.default_headers, **headers}
            mock_post.assert_called_once_with(
                "https://api.example.com/test",
                data={},
                json=None,
                headers=expected_headers,
                timeout=10,
            )

    def test_request_exceptions(self, client):
        with patch("requests.get", side_effect=requests.exceptions.Timeout("Timeout")), patch(
            "src.lib.api.api_logger"
        ) as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                client.get("/test")
            mock_logger.log_failed_call.assert_called_once()

        with patch(
            "requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")
        ), patch("src.lib.api.api_logger") as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                client.get("/test")
            mock_logger.log_failed_call.assert_called_once()

    def test_post_http_error(self, client, mock_response):
        response = mock_response(400, "Bad Request")
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 error")
        with patch("requests.post", return_value=response) as mock_post, patch(
            "src.lib.api.api_logger"
        ) as mock_logger:
            result = client.post("/test", data={})
            assert result == response
            mock_logger.log_failed_call.assert_called_once()

    def test_get_request_with_default_headers(self, client, mock_response):
        response = mock_response(200)
        client.set_default_headers({"User-Agent": "TestClient"})
        with patch("requests.get", return_value=response) as mock_get, patch(
            "src.lib.api.api_logger"
        ):
            client.get("/test")
            mock_get.assert_called_once_with(
                "https://api.example.com/test",
                headers={"User-Agent": "TestClient"},
                params=None,
                timeout=10,
            )

    def test_header_override(self, client, mock_response):
        response = mock_response(200)
        client.set_default_headers({"Content-Type": "xml"})
        with patch("requests.post", return_value=response) as mock_post, patch(
            "src.lib.api.api_logger"
        ):
            client.post("/test", data={}, headers={"Content-Type": "json"})
            mock_post.assert_called_once_with(
                "https://api.example.com/test",
                data={},
                json=None,
                headers={"Content-Type": "json"},
                timeout=10,
            )

    def test_response_time_measurement(self, client, mock_response):
        response = mock_response(200)
        with patch("requests.get", return_value=response), patch(
            "time.time", side_effect=[1000.0, 1002.5]
        ), patch("src.lib.api.api_logger") as mock_logger:
            client.get("/test")
            call_args = mock_logger.log_successful_call.call_args[0][0]
            assert call_args.response_time == 2.5

    def test_logging_successful_call_details(self, client, mock_response):
        response = mock_response(200)
        with patch("requests.get", return_value=response), patch(
            "src.lib.api.api_logger"
        ) as mock_logger:
            client.get("/test", params={"key": "value"})
            log_entry = mock_logger.log_successful_call.call_args[0][0]
            assert log_entry.url == "https://api.example.com/test"
            assert log_entry.method == "GET"
            assert log_entry.response_code.value == 200
            assert log_entry.payload == {"key": "value"}

    def test_logging_failed_call_details(self, client):
        with patch(
            "requests.post", side_effect=requests.exceptions.ConnectionError("fail")
        ), patch("src.lib.api.api_logger") as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                client.post("/test", data={"key": "value"})
            log_entry = mock_logger.log_failed_call.call_args[0][0]
            assert log_entry.url == "https://api.example.com/test"
            assert log_entry.method == "POST"
            assert log_entry.error == "fail"
            assert log_entry.payload == {"key": "value"}
