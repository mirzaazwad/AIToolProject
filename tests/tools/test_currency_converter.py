"""Tests for Currency Converter Tool"""

import pytest
from unittest.mock import Mock, patch
from src.lib.tools.currency_converter import CurrencyConverter
from src.lib.errors.tools.currency_converter import (
    CurrencyAPIError,
    InvalidCurrencyError,
    ConversionRequestError,
    ConversionRateError,
)


class TestCurrencyConverter:
    """Test suite for Currency Converter tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CurrencyConverter()

    def test_successful_conversion(self):
        """Test successful currency conversion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "base": "USD",
            "date": "2024-01-01",
            "rates": {"EUR": 85.23},
        }

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "EUR", "amount": 100.0}
            )
            assert result == "85.23"

    def test_conversion_with_different_currencies(self):
        """Test conversion with different currency pairs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 50.0,
            "base": "GBP",
            "date": "2024-01-01",
            "rates": {"JPY": 6750.5},
        }

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "GBP", "to": "JPY", "amount": 50.0}
            )
            assert result == "6750.5"

    def test_conversion_with_decimal_amount(self):
        """Test conversion with decimal amounts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 25.75,
            "base": "USD",
            "date": "2024-01-01",
            "rates": {"CAD": 34.51},
        }

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "CAD", "amount": 25.75}
            )
            assert result == "34.51"

    def test_missing_from_currency(self):
        """Test error when 'from' currency is missing."""
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: from"
        ):
            self.converter.execute({"to": "EUR", "amount": 100.0})

    def test_missing_to_currency(self):
        """Test error when 'to' currency is missing."""
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: to"
        ):
            self.converter.execute({"from": "USD", "amount": 100.0})

    def test_missing_amount(self):
        """Test error when amount is missing."""
        with pytest.raises(
            ConversionRequestError, match="Missing required parameter: amount"
        ):
            self.converter.execute({"from": "USD", "to": "EUR"})

    def test_invalid_amount_type(self):
        """Test error when amount is not a number."""
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": "invalid"})

    def test_negative_amount(self):
        """Test error when amount is negative."""
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": -100.0})

    def test_zero_amount(self):
        """Test error when amount is zero."""
        with pytest.raises(
            ConversionRequestError, match="Amount must be a positive number"
        ):
            self.converter.execute({"from": "USD", "to": "EUR", "amount": 0})

    def test_invalid_currency_code(self):
        """Test error when currency code is invalid."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid currency code"

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(InvalidCurrencyError, match="Invalid currency code"):
                self.converter.execute(
                    {"from": "INVALID", "to": "EUR", "amount": 100.0}
                )

    def test_api_server_error(self):
        """Test handling of API server errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(CurrencyAPIError, match="Currency API error"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_missing_conversion_rate(self):
        """Test error when conversion rate is missing from response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "base": "USD",
            "date": "2024-01-01",
            "rates": {},
        }

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(ConversionRateError, match="Conversion rate not found"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_malformed_api_response(self):
        """Test handling of malformed API responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            with pytest.raises(CurrencyAPIError, match="Invalid API response format"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_network_error(self):
        """Test handling of network errors."""
        with patch.object(
            self.converter.apiClient, "get", side_effect=Exception("Network error")
        ):
            with pytest.raises(CurrencyAPIError, match="Currency conversion failed"):
                self.converter.execute({"from": "USD", "to": "EUR", "amount": 100.0})

    def test_same_currency_conversion(self):
        """Test conversion between same currencies."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "base": "USD",
            "date": "2024-01-01",
            "rates": {"USD": 100.0},
        }

        with patch.object(self.converter.apiClient, "get", return_value=mock_response):
            result = self.converter.execute(
                {"from": "USD", "to": "USD", "amount": 100.0}
            )
            assert result == "100.0"
