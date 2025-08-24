"""Schema for System Metrics"""

from pydantic import BaseModel, Field
from typing import Dict


class AgentMetrics(BaseModel):
    """Metrics for agent operations."""

    queries_processed: int = Field(
        default=0, description="Total number of queries processed"
    )
    successful_responses: int = Field(
        default=0, description="Number of successful responses"
    )
    failed_responses: int = Field(default=0, description="Number of failed responses")
    parsing_errors: int = Field(default=0, description="Number of parsing errors")
    workflow_errors: int = Field(default=0, description="Number of workflow errors")
    average_processing_time: float = Field(
        default=0.0, description="Average processing time in seconds"
    )
    total_processing_time: float = Field(
        default=0.0, description="Total processing time in seconds"
    )


class ToolMetrics(BaseModel):
    """Metrics for tool operations."""

    tool_calls: int = Field(default=0, description="Total number of tool calls")
    successful_calls: int = Field(
        default=0, description="Number of successful tool calls"
    )
    failed_calls: int = Field(default=0, description="Number of failed tool calls")
    tool_usage: Dict[str, int] = Field(
        default_factory=dict, description="Usage count per tool"
    )
    execution_sequence: list[str] = Field(
        default_factory=list, description="Sequence of tool executions"
    )


class APIMetrics(BaseModel):
    """Metrics for API operations."""

    total_calls: int = Field(default=0, description="Total number of API calls")
    successful_calls: int = Field(
        default=0, description="Number of successful API calls"
    )
    failed_calls: int = Field(default=0, description="Number of failed API calls")
    total_response_time: float = Field(
        default=0.0, description="Total response time in seconds"
    )
    average_response_time: float = Field(
        default=0.0, description="Average response time in seconds"
    )
