"""Currency Converter Tool"""

from .base import Action
from ..api import ApiClient
from ...constants.tools import CURRENCY_API_URL
from ...data.schemas.tools.currency import (
    CurrencyConversionRequest,
    CurrencyConversionResponse,
)
from ..errors.tools.currency_converter import (
    CurrencyAPIError,
    InvalidCurrencyError,
    ConversionRequestError,
    ConversionRateError,
)


class CurrencyConverter(Action):
    """Currency converter tool using Frankfurter API."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=CURRENCY_API_URL)

    def execute(self, args: dict) -> str:
        """
        Execute currency conversion.
        """
        try:
            request = CurrencyConversionRequest(**args)
            raw_response = self._fetch_conversion_data(request)
            response = self._parse_response(raw_response)
            converted_amount = self._get_converted_amount(request, response)
            return str(converted_amount)

        except (InvalidCurrencyError, CurrencyAPIError, ConversionRateError):
            raise
        except ValueError as e:
            raise self._handle_value_error(e)
        except Exception as e:
            raise CurrencyAPIError(f"Currency conversion failed: {str(e)}")

    def _fetch_conversion_data(self, request: CurrencyConversionRequest):
        """Fetch conversion data from API and handle HTTP errors."""
        raw_response = self.apiClient.get("/latest", params=request.to_query_params())

        if raw_response.status_code == 400:
            raise InvalidCurrencyError("Invalid currency code provided")
        if raw_response.status_code != 200:
            raise CurrencyAPIError(
                f"Currency API error: {raw_response.status_code} - {raw_response.text}"
            )
        return raw_response

    def _parse_response(self, raw_response) -> CurrencyConversionResponse:
        """Parse API JSON response safely."""
        try:
            return CurrencyConversionResponse(**raw_response.json())
        except ValueError as e:
            raise CurrencyAPIError(f"Invalid API response format: {str(e)}")

    def _get_converted_amount(
        self, request: CurrencyConversionRequest, response: CurrencyConversionResponse
    ) -> float:
        """Extract and validate the converted amount."""
        converted_amount = response.get_converted_amount(request.to_currency)
        if converted_amount == 0.0:
            raise ConversionRateError(
                f"Conversion rate not found for {request.to_currency}"
            )
        return converted_amount

    def _handle_value_error(self, e: ValueError) -> ConversionRequestError:
        """Map Pydantic validation errors to domain-specific errors."""
        error_msg = str(e)
        if "Field required" in error_msg:
            missing_field = self._extract_missing_field(error_msg)
            return ConversionRequestError(
                f"Missing required parameter: {missing_field}"
            )
        if "Input should be greater than 0" in error_msg:
            return ConversionRequestError("Amount must be a positive number")
        if "Input should be a valid number" in error_msg:
            return ConversionRequestError("Amount must be a positive number")
        return ConversionRequestError(f"Invalid conversion request: {error_msg}")

    def _extract_missing_field(self, error_msg: str) -> str:
        """Extract which field was missing from error message."""
        for line in error_msg.split("\n"):
            line = line.strip()
            if line in {"from", "to", "amount"}:
                return line
        return "unknown"
