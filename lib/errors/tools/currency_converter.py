"""Currency converter tool specific exceptions."""


class CurrencyConverterError(Exception):
    """Base exception for currency converter errors."""
    def __init__(self, message: str = "Currency converter error occurred"):
        self.message = message
        super().__init__(self.message)


class CurrencyAPIError(CurrencyConverterError):
    """Exception raised for currency API related errors."""
    def __init__(self, message: str = "Currency API error"):
        self.message = message
        super().__init__(self.message)


class InvalidCurrencyError(CurrencyConverterError):
    """Exception raised for invalid currency codes."""
    def __init__(self, message: str = "Invalid currency code"):
        self.message = message
        super().__init__(self.message)


class ConversionRequestError(CurrencyConverterError):
    """Exception raised for invalid conversion requests."""
    def __init__(self, message: str = "Invalid conversion request"):
        self.message = message
        super().__init__(self.message)


class ConversionRateError(CurrencyConverterError):
    """Exception raised when conversion rates are not available."""
    def __init__(self, message: str = "Conversion rate not available"):
        self.message = message
        super().__init__(self.message)
