"""Currency Converter Tool"""
from .base import Action
from ..api import ApiClient
from ...constants.tools import CURRENCY_API_URL
from ...data.schemas.tools.currency import CurrencyConversionRequest, CurrencyConversionResponse
from ..errors.tools.currency_converter import (
    CurrencyAPIError,
    InvalidCurrencyError,
    ConversionRequestError,
    ConversionRateError
)

class CurrencyConverter(Action):
    """Currency converter tool using Frankfurter API."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=CURRENCY_API_URL)

    def execute(self, args: dict) -> str:
        """
        Execute currency conversion.

        Args:
            args: Dictionary containing 'from', 'to', and 'amount' keys

        Returns:
            Converted amount as string
        """
        try:

            request = CurrencyConversionRequest(**args)


            raw_response = self.apiClient.get("/latest", params=request.to_query_params())


            if raw_response.status_code == 400:
                raise InvalidCurrencyError("Invalid currency code provided")
            elif raw_response.status_code != 200:
                raise CurrencyAPIError(f"Currency API error: {raw_response.status_code} - {raw_response.text}")


            response = CurrencyConversionResponse(**raw_response.json())


            converted_amount = response.get_converted_amount(request.to_currency)
            if converted_amount is None:
                raise ConversionRateError(f"Conversion rate not available for {request.to_currency}")

            return str(converted_amount)
        except ValueError as e:
            raise ConversionRequestError(f"Invalid conversion request: {str(e)}")
