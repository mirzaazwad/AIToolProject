class InvokerError(Exception):
    """Base exception for tool invoker errors."""
    def __init__(self, message: str = "Tool invoker error occurred"):
        self.message = message
        super().__init__(self.message)