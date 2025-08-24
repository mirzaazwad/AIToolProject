"""Calculator tool specific exceptions."""


class CalculatorError(Exception):
    """Base exception for calculator errors."""

    def __init__(self, message: str = "Calculator error occurred"):
        self.message = message
        super().__init__(self.message)


class ExpressionError(CalculatorError):
    """Exception raised for invalid mathematical expressions."""

    def __init__(self, message: str = "Invalid mathematical expression"):
        self.message = message
        super().__init__(self.message)


class TokenizationError(CalculatorError):
    """Exception raised for errors during expression tokenization."""

    def __init__(self, message: str = "Error tokenizing expression"):
        self.message = message
        super().__init__(self.message)


class EvaluationError(CalculatorError):
    """Exception raised for errors during expression evaluation."""

    def __init__(self, message: str = "Error evaluating expression"):
        self.message = message
        super().__init__(self.message)


class BracketMismatchError(CalculatorError):
    """Exception raised for mismatched brackets in expressions."""

    def __init__(self, message: str = "Mismatched brackets in expression"):
        self.message = message
        super().__init__(self.message)
