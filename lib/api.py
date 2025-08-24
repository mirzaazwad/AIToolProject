"""Generic API Client"""
import requests
import time
from typing import Dict, Any, Optional, Union
from lib.loggers import api_logger
from data.schemas.api_logging import SuccessfulAPICallLog, FailedAPICallLog
from constants.api import StatusCodes


class ApiClient:
    """
    A generic API client that handles GET and POST requests
    with standardized logging and error handling.
    """

    def __init__(self, base_url: str = "", default_headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all requests (optional)
            default_headers: Default headers for all requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        """Build a full URL from the base URL and endpoint."""
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint

    def _merge_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge default headers with request-specific headers."""
        merged = {**self.default_headers}
        if headers:
            merged.update(headers)
        return merged

    def _log_success(self, url: str, method: str, response: requests.Response, payload: Optional[Dict[str, Any]], elapsed: float) -> None:
        """Log successful API call."""
        log_data = SuccessfulAPICallLog(
            url=url,
            method=method,
            response_code=response.status_code,
            response_time=elapsed,
            payload=payload
        )
        api_logger.log_successful_call(log_data)

    def _log_failure(self, url: str, method: str, error: str, payload: Optional[Dict[str, Any]], status_code: int, elapsed: float) -> None:
        """Log failed API call."""
        log_data = FailedAPICallLog(
            url=url,
            error=error,
            method=method,
            payload=payload,
            response_code=status_code,
            response_time=elapsed
        )
        api_logger.log_failed_call(log_data)

    def _handle_request_exception(self, e: requests.RequestException) -> int:
        """Extract status code from exception if available."""
        return getattr(e.response, "status_code", 500) if hasattr(e, "response") and e.response else 500

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform a GET request.

        Args:
            endpoint: Relative or absolute API endpoint
            params: Query parameters
            headers: Optional request-specific headers

        Returns:
            Response object

        Raises:
            requests.RequestException
        """
        url = self._build_url(endpoint)
        request_headers = self._merge_headers(headers)
        start_time = time.time()

        try:
            response = requests.get(url, params=params, headers=request_headers, timeout=self.timeout)
            elapsed = time.time() - start_time
            payload = params

            if response.status_code < StatusCodes.BAD_REQUEST.value:
                self._log_success(url, "GET", response, payload, elapsed)
            else:
                self._log_failure(url, "GET", response.text, payload, response.status_code, elapsed)

            return response
        except requests.RequestException as e:
            elapsed = time.time() - start_time
            status_code = self._handle_request_exception(e)
            self._log_failure(url, "GET", str(e), params, status_code, elapsed)
            raise requests.RequestException(f"GET request failed for {url}: {str(e)}") from e

    def post(self,
             endpoint: str,
             data: Optional[Union[Dict[str, Any], str]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform a POST request.

        Args:
            endpoint: Relative or absolute API endpoint
            data: Form or raw data
            json_data: JSON body (overrides data if present)
            headers: Optional request-specific headers

        Returns:
            Response object

        Raises:
            requests.RequestException
        """
        url = self._build_url(endpoint)
        request_headers = self._merge_headers(headers)

        if json_data and "Content-Type" not in request_headers:
            request_headers["Content-Type"] = "application/json"

        payload = json_data if json_data is not None else data
        start_time = time.time()

        try:
            response = requests.post(url, data=data, json=json_data, headers=request_headers, timeout=self.timeout)
            elapsed = time.time() - start_time
            payload_dict = payload if isinstance(payload, dict) else None

            if response.status_code < StatusCodes.BAD_REQUEST.value:
                self._log_success(url, "POST", response, payload_dict, elapsed)
            else:
                self._log_failure(url, "POST", response.text, payload_dict, response.status_code, elapsed)

            return response
        except requests.RequestException as e:
            elapsed = time.time() - start_time
            status_code = self._handle_request_exception(e)
            payload_dict = payload if isinstance(payload, dict) else None
            self._log_failure(url, "POST", str(e), payload_dict, status_code, elapsed)
            raise requests.RequestException(f"POST request failed for {url}: {str(e)}") from e

    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """Set global default headers for requests."""
        self.default_headers.update(headers)

    def set_auth_header(self, token: str, auth_type: str = "Bearer") -> None:
        """Set a global authentication header."""
        self.default_headers["Authorization"] = f"{auth_type} {token}"
