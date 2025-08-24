"""OpenAI LLM specific exceptions."""


class OpenAIError(Exception):
    """Base exception for OpenAI LLM errors."""
    def __init__(self, message: str = "OpenAI LLM error occurred"):
        self.message = message
        super().__init__(self.message)
