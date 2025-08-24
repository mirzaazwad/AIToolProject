"""Gemini LLM specific exceptions."""


class GeminiError(Exception):
    """Base exception for Gemini LLM errors."""
    def __init__(self, message: str = "Gemini LLM error occurred"):
        self.message = message
        super().__init__(self.message)
