"""Schema for Currency Conversion"""

from typing import Dict, Union

from pydantic import BaseModel, Field, field_validator


class CurrencyConversionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to convert")
    from_currency: str = Field(..., alias="from", description="Source currency code")
    to_currency: str = Field(..., alias="to", description="Target currency code")

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    def to_query_params(self) -> dict[str, Union[str, float]]:
        """Convert to query parameters for API request."""
        return {
            "amount": self.amount,
            "from": self.from_currency,
            "to": self.to_currency,
        }


class CurrencyConversionResponse(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to convert")
    base: str = Field(..., description="Base currency code")
    date: str = Field(..., description="Date of conversion")
    rates: Dict[str, float] = Field(..., description="Currency code with amount")

    def get_converted_amount(self, to_currency: str) -> float:
        """Get the converted amount for the specified currency."""
        return self.rates.get(to_currency, 0.0)

    def get_conversion_rate(self, to_currency: str) -> float:
        """Get the conversion rate for the specified currency."""
        return self.rates.get(to_currency, 0.0) / self.amount
