"""Tests for API Client"""

import pytest
from unittest.mock import Mock, patch
import requests
from src.lib.api import ApiClient


class TestApiClient:
    """Test suite for API Client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ApiClient(base_url="https://api.example.com", timeout=10)

    def test_initialization_with_defaults(self):
        """Test API client initialization with default values."""
        client = ApiClient()

        assert client.base_url == ""
        assert client.default_headers == {}
        assert client.timeout == 30

    def test_initialization_with_custom_values(self):
        """Test API client initialization with custom values."""
        headers = {"Authorization": "Bearer token"}
        client = ApiClient(
            base_url="https://custom.api.com/", default_headers=headers, timeout=60
        )

        assert client.base_url == "https://custom.api.com"
        assert client.default_headers == headers
        assert client.timeout == 60

    def test_build_url_with_base_url(self):
        """Test URL building with base URL."""
        url = self.client._build_url("/endpoint")
        assert url == "https://api.example.com/endpoint"

        url = self.client._build_url("endpoint")
        assert url == "https://api.example.com/endpoint"

    def test_build_url_without_base_url(self):
        """Test URL building without base URL."""
        client = ApiClient()
        url = client._build_url("https://full.url.com/endpoint")
        assert url == "https://full.url.com/endpoint"

    def test_set_default_headers(self):
        """Test setting default headers."""
        headers = {"Content-Type": "application/json", "User-Agent": "TestClient"}
        self.client.set_default_headers(headers)

        assert self.client.default_headers == headers

    def test_set_auth_header_bearer(self):
        """Test setting Bearer authorization header."""
        self.client.set_auth_header("test_token", "Bearer")

        assert self.client.default_headers["Authorization"] == "Bearer test_token"

    def test_set_auth_header_api_key(self):
        """Test setting API key authorization header."""
        self.client.set_auth_header("test_key", "ApiKey")

        assert self.client.default_headers["Authorization"] == "ApiKey test_key"

    def test_set_auth_header_custom(self):
        """Test setting custom authorization header."""
        self.client.set_auth_header("custom_value", "Custom")

        assert self.client.default_headers["Authorization"] == "Custom custom_value"

    @patch("requests.get")
    def test_successful_get_request(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        with patch("src.lib.api.api_logger") as mock_logger:
            response = self.client.get("/test")

            assert response == mock_response
            mock_get.assert_called_once_with(
                "https://api.example.com/test", headers={}, params=None, timeout=10
            )
            mock_logger.log_successful_call.assert_called_once()

    @patch("requests.get")
    def test_get_request_with_params_and_headers(self, mock_get):
        """Test GET request with parameters and headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        params = {"key": "value", "limit": 10}
        headers = {"Custom-Header": "custom-value"}

        with patch("src.lib.api.api_logger"):
            self.client.get("/test", params=params, headers=headers)

            expected_headers = {**self.client.default_headers, **headers}
            mock_get.assert_called_once_with(
                "https://api.example.com/test",
                headers=expected_headers,
                params=params,
                timeout=10,
            )

    @patch("requests.post")
    def test_successful_post_request(self, mock_post):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Created"
        mock_post.return_value = mock_response

        data = {"name": "test", "value": 123}

        with patch("src.lib.api.api_logger") as mock_logger:
            response = self.client.post("/create", data=data)

            assert response == mock_response
            mock_post.assert_called_once_with(
                "https://api.example.com/create",
                data=data,
                json=None,
                headers={},
                timeout=10,
            )
            mock_logger.log_successful_call.assert_called_once()

    @patch("requests.post")
    def test_post_request_with_headers(self, mock_post):
        """Test POST request with custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {"test": "data"}
        headers = {"Content-Type": "application/json"}

        with patch("src.lib.api.api_logger"):
            self.client.post("/test", data=data, headers=headers)

            expected_headers = {**self.client.default_headers, **headers}
            mock_post.assert_called_once_with(
                "https://api.example.com/test",
                data=data,
                json=None,
                headers=expected_headers,
                timeout=10,
            )

    @patch("requests.get")
    def test_get_request_timeout(self, mock_get):
        """Test GET request timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        with patch("src.lib.api.api_logger") as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                self.client.get("/test")

            mock_logger.log_failed_call.assert_called_once()

    @patch("requests.get")
    def test_get_request_connection_error(self, mock_get):
        """Test GET request connection error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with patch("src.lib.api.api_logger") as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                self.client.get("/test")

            mock_logger.log_failed_call.assert_called_once()

    @patch("requests.post")
    def test_post_request_http_error(self, mock_post):
        """Test POST request HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error"
        )
        mock_post.return_value = mock_response

        with patch("src.lib.api.api_logger") as mock_logger:
            response = self.client.post("/test", data={})

            assert response == mock_response
            mock_logger.log_failed_call.assert_called_once()

    @patch("requests.get")
    def test_get_request_with_default_headers(self, mock_get):
        """Test GET request uses default headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        default_headers = {"User-Agent": "TestClient", "Accept": "application/json"}
        self.client.set_default_headers(default_headers)

        with patch("src.lib.api.api_logger"):
            self.client.get("/test")

            mock_get.assert_called_once_with(
                "https://api.example.com/test",
                headers=default_headers,
                params=None,
                timeout=10,
            )

    @patch("requests.post")
    def test_post_request_header_override(self, mock_post):
        """Test POST request header override."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.client.set_default_headers({"Content-Type": "application/xml"})

        request_headers = {"Content-Type": "application/json"}

        with patch("src.lib.api.api_logger"):
            self.client.post("/test", data={}, headers=request_headers)

            expected_headers = {"Content-Type": "application/json"}
            mock_post.assert_called_once_with(
                "https://api.example.com/test",
                data={},
                json=None,
                headers=expected_headers,
                timeout=10,
            )

    def test_response_time_measurement(self):
        """Test that response time is measured correctly."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            with patch("time.time", side_effect=[1000.0, 1002.5]):
                with patch("src.lib.api.api_logger") as mock_logger:
                    self.client.get("/test")

                    mock_logger.log_successful_call.assert_called_once()
                    call_args = mock_logger.log_successful_call.call_args[0][0]
                    assert call_args.response_time == 2.5

    @patch("requests.get")
    def test_logging_successful_call_details(self, mock_get):
        """Test that successful calls are logged with correct details."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch("src.lib.api.api_logger") as mock_logger:
            self.client.get("/test", params={"key": "value"})

            mock_logger.log_successful_call.assert_called_once()
            log_entry = mock_logger.log_successful_call.call_args[0][0]

            assert log_entry.url == "https://api.example.com/test"
            assert log_entry.method == "GET"
            assert log_entry.response_code.value == 200
            assert log_entry.payload == {"key": "value"}

    @patch("requests.post")
    def test_logging_failed_call_details(self, mock_post):
        """Test that failed calls are logged with correct details."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with patch("src.lib.api.api_logger") as mock_logger:
            with pytest.raises(requests.exceptions.RequestException):
                self.client.post("/test", data={"key": "value"})

            mock_logger.log_failed_call.assert_called_once()
            log_entry = mock_logger.log_failed_call.call_args[0][0]

            assert log_entry.url == "https://api.example.com/test"
            assert log_entry.method == "POST"
            assert log_entry.error == "Connection failed"
            assert log_entry.payload == {"key": "value"}
