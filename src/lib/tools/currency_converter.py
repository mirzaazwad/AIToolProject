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

        Args:
            args: Dictionary containing 'from', 'to', and 'amount' keys

        Returns:
            Converted amount as string
        """
        try:
            request = CurrencyConversionRequest(**args)

            raw_response = self.apiClient.get(
                "/latest", params=request.to_query_params()
            )

            if raw_response.status_code == 400:
                raise InvalidCurrencyError("Invalid currency code provided")
            elif raw_response.status_code != 200:
                raise CurrencyAPIError(
                    f"Currency API error: {raw_response.status_code} - {raw_response.text}"
                )

            try:
                response = CurrencyConversionResponse(**raw_response.json())
            except ValueError as e:
                raise CurrencyAPIError(f"Invalid API response format: {str(e)}")

            converted_amount = response.get_converted_amount(request.to_currency)
            if converted_amount == 0.0:
                raise ConversionRateError(
                    f"Conversion rate not found for {request.to_currency}"
                )

            return str(converted_amount)

        except (InvalidCurrencyError, CurrencyAPIError, ConversionRateError):
            raise
        except ValueError as e:
            error_msg = str(e)
            if "Field required" in error_msg:
                lines = error_msg.split("\n")
                for line in lines:
                    line = line.strip()
                    if line == "from":
                        raise ConversionRequestError("Missing required parameter: from")
                    elif line == "to":
                        raise ConversionRequestError("Missing required parameter: to")
                    elif line == "amount":
                        raise ConversionRequestError(
                            "Missing required parameter: amount"
                        )
                raise ConversionRequestError("Missing required parameter")
            elif "Input should be greater than 0" in error_msg:
                raise ConversionRequestError("Amount must be a positive number")
            elif "Input should be a valid number" in error_msg:
                raise ConversionRequestError("Amount must be a positive number")
            else:
                raise ConversionRequestError(f"Invalid conversion request: {error_msg}")
        except Exception as e:
            raise CurrencyAPIError(f"Currency conversion failed: {str(e)}")
