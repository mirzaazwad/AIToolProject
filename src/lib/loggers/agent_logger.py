"""
Agent-specific logger for tracking high-level agent operations and workflows.
"""

from .base import BaseLogger
from ...data.schemas.logging.metrics import AgentMetrics


class AgentLogger(BaseLogger):
    """Logger specialized for agent operations and workflows."""

    def __init__(self, level: str = "INFO"):
        super().__init__("agent", "agent.log", level)

        if not hasattr(self, "metrics"):
            self.metrics = AgentMetrics()

    def log_query_start(self, query: str, session_id: str = None) -> None:
        """Log the start of query processing."""
        self.metrics.queries_processed += 1

        session_info = f" [Session: {session_id}]" if session_id else ""
        self.info(f"QUERY_START{session_info}: {query}")

    def log_query_success(
        self, query: str, response: str, processing_time: float = 0.0
    ) -> None:
        """Log successful query completion."""
        self.metrics.successful_responses += 1
        self.metrics.total_processing_time += processing_time
        self._update_average_processing_time()

        response_str = str(response)
        if len(response_str) > 300:
            response_str = response_str[:300] + "..."

        self.info(
            f"QUERY_SUCCESS: '{query[:50]}...' completed in {processing_time:.2f}s"
        )
        self.debug(f"Response: {response_str}")

    def log_query_failure(
        self, query: str, error: str, processing_time: float = 0.0
    ) -> None:
        """Log failed query processing."""
        self.metrics.failed_responses += 1
        self.metrics.total_processing_time += processing_time
        self._update_average_processing_time()

        self.error(
            f"QUERY_FAILED: '{query[:50]}...' - {error} (took {processing_time:.2f}s)"
        )

    def log_llm_interaction(
        self, prompt: str, response: str, model: str = "unknown"
    ) -> None:
        """Log LLM interactions."""
        prompt_str = prompt[:200] + "..." if len(prompt) > 200 else prompt
        response_str = response[:200] + "..." if len(response) > 200 else response

        self.debug(f"LLM_INTERACTION [{model}]: Prompt: {prompt_str}")
        self.debug(f"LLM_RESPONSE [{model}]: {response_str}")

    def log_parsing_error(self, response: str, error: str) -> None:
        """Log LLM response parsing error."""
        self.metrics.parsing_errors += 1

        response_str = response[:200] + "..." if len(response) > 200 else response

        self.warning(f"PARSING_ERROR: {error}")
        self.debug(f"Problematic response: {response_str}")

    def log_workflow_step(self, step: str, details: str = None) -> None:
        """Log workflow step execution."""
        message = f"WORKFLOW_STEP: {step}"
        if details:
            message += f" - {details}"
        self.info(message)

    def log_workflow_error(self, step: str, error: str) -> None:
        """Log workflow execution error."""
        self.metrics.workflow_errors += 1

        self.error(f"WORKFLOW_ERROR: {step} - {error}")

    def log_tool_plan(self, tools: list[dict[str, str | list[str]]]) -> None:
        """Log the planned tool execution sequence."""
        tool_names = [tool.get("tool", "unknown") for tool in tools]
        self.info(f"TOOL_PLAN: Executing tools in sequence: {' -> '.join(tool_names)}")

        for i, tool in enumerate(tools):
            dependencies = tool.get("depends_on", [])
            dep_info = f" (depends on: {dependencies})" if dependencies else ""
            self.debug(f"  {i+1}. {tool.get('tool', 'unknown')}{dep_info}")

    def log_recursive_execution(self, iteration: int, reason: str) -> None:
        """Log recursive tool execution."""
        self.info(f"RECURSIVE_EXECUTION: Iteration {iteration} - {reason}")

    def log_session_start(self, session_id: str) -> None:
        """Log session start."""
        self.info(f"SESSION_START: {session_id}")

    def log_session_end(self, session_id: str, duration: float = 0.0) -> None:
        """Log session end."""
        self.info(f"SESSION_END: {session_id} (duration: {duration:.2f}s)")

    def _update_average_processing_time(self) -> None:
        """Update the average processing time metric."""
        total_queries = (
            self.metrics.successful_responses + self.metrics.failed_responses
        )
        if total_queries > 0:
            self.metrics.average_processing_time = (
                self.metrics.total_processing_time / total_queries
            )

    def get_metrics(self) -> AgentMetrics:
        """Get current agent metrics."""
        return self.metrics.model_copy()
