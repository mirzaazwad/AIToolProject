"""
API-specific logger for tracking API calls and responses.
"""

from .base import BaseLogger
from ...data.schemas.logging.api_logging import SuccessfulAPICallLog, FailedAPICallLog
from ...data.schemas.logging.metrics import APIMetrics


class ApiLogger(BaseLogger):
    """Logger specialized for API operations."""

    def __init__(self, level: str = "INFO"):
        super().__init__("api", "api.log", level)

        if not hasattr(self, "metrics"):
            self.metrics = APIMetrics()

    def log_successful_call(self, log_data: SuccessfulAPICallLog) -> None:
        """Log successful API call using schema."""
        self.metrics.total_calls += 1
        self.metrics.successful_calls += 1
        self.metrics.total_response_time += log_data.response_time
        self._update_average_response_time()
        self.info(
            f"{log_data.method} {log_data.url} - {log_data.response_code.value} {log_data.response_code.name} payload: {str(log_data.payload)[:50]+'...' if len(str(str(log_data.payload))) > 50 else str(log_data.payload)} ({log_data.response_time:.2f}s)"
        )

    def log_failed_call(self, log_data: FailedAPICallLog) -> None:
        """Log failed API call using schema."""
        self.metrics.total_calls += 1
        self.metrics.failed_calls += 1
        self.metrics.total_response_time += log_data.response_time
        self._update_average_response_time()
        self.error(
            f"{log_data.method} {log_data.url} - {log_data.error} {log_data.response_code.value} {log_data.response_code.name} payload: {str(log_data.payload)[:50]+'...' if len(str(str(log_data.payload))) > 50 else str(log_data.payload)} ({log_data.response_time:.2f}s)"
        )

    def _update_average_response_time(self) -> None:
        """Update the average response time metric."""
        if self.metrics.total_calls > 0:
            self.metrics.average_response_time = (
                self.metrics.total_response_time / self.metrics.total_calls
            )

    def get_metrics(self) -> APIMetrics:
        """Get current API metrics."""
        return self.metrics.model_copy()
