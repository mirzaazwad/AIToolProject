"""Tests for Currency Converter Tool"""

from unittest.mock import Mock, patch

import pytest

from src.lib.errors.tools.currency_converter import (ConversionRateError,
                                                     ConversionRequestError,
                                                     CurrencyAPIError,
                                                     InvalidCurrencyError)
from src.lib.tools.currency_converter import CurrencyConverter


@pytest.mark.usefixtures("converter_fixture")
class TestCurrencyConverter:
    """Test suite for Currency Converter tool."""

    @pytest.fixture(autouse=True)
    def converter_fixture(self):
        """Fixture that provides a CurrencyConverter instance for each test."""
        self.converter = CurrencyConverter()

    def _mock_response(self, status_code=200, json_data=None, text=None):
        """Helper to create a mock API response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        if json_data is not None:
            mock_response.json.return_value = json_data
        if text is not None:
            mock_response.text = text
        return mock_response

    def test_successful_conversion(self):
        mock_response = self._mock_response(
            200,
            {
                "amount": 100.0,
                "base": "USD",
                "date": "2024-01-01",
                "rates": {"EUR": 85.23},
            },
        )
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "EUR", "amount": 100.0}
            )
            assert result == "85.23"

    def test_conversion_with_different_currencies(self):
        mock_response = self._mock_response(
            200,
            {
                "amount": 50.0,
                "base": "GBP",
                "date": "2024-01-01",
                "rates": {"JPY": 6750.5},
            },
        )
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "GBP", "to": "JPY", "amount": 50.0}
            )
            assert result == "6750.5"

    def test_conversion_with_decimal_amount(self):
        mock_response = self._mock_response(
            200,
            {
                "amount": 25.75,
                "base": "USD",
                "date": "2024-01-01",
                "rates": {"CAD": 34.51},
            },
        )
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "CAD", "amount": 25.75}
            )
            assert result == "34.51"

    def test_missing_from_currency(self):
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: from"
        ):
            self.converter.execute({"to": "EUR", "amount": 100.0})

    def test_missing_to_currency(self):
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: to"
        ):
            self.converter.execute({"from": "USD", "amount": 100.0})

    def test_missing_amount(self):
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: amount"
        ):
            self.converter.execute({"from": "USD", "to": "EUR"})

    def test_invalid_amount_type(self):
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": "invalid"})

    def test_negative_amount(self):
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": -100.0})

    def test_zero_amount(self):
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": 0})

    def test_invalid_currency_code(self):
        mock_response = self._mock_response(400, text="Invalid currency code")
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(InvalidCurrencyError, match="Invalid currency code"):
                self.converter.execute(
                    {"from": "INVALID", "to": "EUR", "amount": 100.0}
                )

    def test_api_server_error(self):
        mock_response = self._mock_response(500, text="Internal server error")
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(CurrencyAPIError, match="Currency API error"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_missing_conversion_rate(self):
        mock_response = self._mock_response(
            200,
            {"amount": 100.0, "base": "USD", "date": "2024-01-01", "rates": {}},
        )
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(ConversionRateError, match="Conversion rate not found"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_malformed_api_response(self):
        mock_response = self._mock_response(200, {"invalid": "response"})
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(CurrencyAPIError, match="Invalid API response format"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_network_error(self):
        with patch.object(
            self.converter.apiClient, "get", side_effect=Exception("Network error")
        ):
            with pytest.raises(CurrencyAPIError, match="Currency conversion failed"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_same_currency_conversion(self):
        mock_response = self._mock_response(
            200,
            {
                "amount": 100.0,
                "base": "USD",
                "date": "2024-01-01",
                "rates": {"USD": 100.0},
            },
        )
        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "USD", "amount": 100.0}
            )
            assert result == "100.0"
