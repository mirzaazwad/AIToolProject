"""Schema for Tool Response"""

from pydantic import BaseModel, Field
from typing import Optional, Union


class ToolResponse(BaseModel):
    """Represents a response from a tool execution."""

    tool: str = Field(..., description="Name of the tool that was executed")
    args: dict[str, Union[str, float, int]] = Field(
        ..., description="Arguments passed to the tool"
    )
    result: Optional[str] = Field(None, description="Result from tool execution")
    success: bool = Field(..., description="Whether the tool execution was successful")
    error: Optional[str] = Field(None, description="Error message if execution failed")

    def is_successful(self) -> bool:
        """Check if the tool execution was successful."""
        return self.success and self.result is not None

    def get_result_or_error(self) -> str:
        """Get the result if successful, otherwise return the error message."""
        if self.success and self.result is not None:
            return self.result
        return self.error or "Unknown error occurred"
