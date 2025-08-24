"""Schemas for API call logging."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Union
from constants.api import StatusCodes


class SuccessfulAPICallLog(BaseModel):
    """Schema for logging successful API calls."""
    url: str = Field(..., description="The API endpoint URL")
    method: str = Field(default="GET", description="HTTP method used")
    response_code: StatusCodes = Field(default=StatusCodes.OK, description="HTTP response status code")
    response_time: float = Field(default=0.0, description="Response time in seconds")
    payload: Optional[Dict[str, Union[str, int, float, bool, list, dict]]] = Field(
        default=None, 
        description="Request payload data"
    )


class FailedAPICallLog(BaseModel):
    """Schema for logging failed API calls."""
    url: str = Field(..., description="The API endpoint URL")
    error: str = Field(..., description="Error message or description")
    method: str = Field(default="GET", description="HTTP method used")
    payload: Optional[Dict[str, Union[str, int, float, bool, list, dict]]] = Field(
        default=None, 
        description="Request payload data"
    )
    response_code: StatusCodes = Field(default=StatusCodes.INTERNAL_SERVER_ERROR, description="HTTP response status code")
    response_time: float = Field(default=0.0, description="Response time in seconds")
