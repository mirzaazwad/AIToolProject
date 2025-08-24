from lib.llm.base import LLMStrategy
from lib.tools.tool_invoker import ToolInvokerBase
from constants.messages import FAILED_AGENT_MESSAGE
from constants.llm import FUSE_FORMAT_MESSAGE
from data.schemas.tool import ToolPlan
from lib.loggers import agent_logger
from typing import List, Dict, Any
from abc import ABC
import time
import re


class Agent(ABC):
    """Abstract base class implementing the Template Method pattern for agents."""

    def __init__(self, llm_strategy: LLMStrategy, tool_invoker: ToolInvokerBase):
        self.llm_strategy = llm_strategy
        self.tool_invoker = tool_invoker

    def answer(self, query: str) -> str:
        """
        Template method that defines the algorithm for answering queries.
        This method cannot be overridden by subclasses.
        """
        start_time = time.time()
        agent_logger.log_query_start(query)

        try:
            processed_query = self.preprocess_query(query)
            tool_plan = self.get_tool_suggestions(processed_query)
            self.tool_plan = [suggestion.model_dump() for suggestion in tool_plan.suggestions]
            agent_logger.log_tool_plan([suggestion.model_dump() for suggestion in tool_plan.suggestions])

            tool_responses = self.execute_tools(tool_plan)
            processed_responses = self.postprocess_responses(tool_responses)
            result = self.fuse_responses(processed_responses, processed_query)

            processing_time = time.time() - start_time
            agent_logger.log_query_success(query, result, processing_time)

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            agent_logger.log_query_failure(query, str(e), processing_time)
            return FAILED_AGENT_MESSAGE

    def get_tool_suggestions(self, query: str) -> ToolPlan:
        """Get tool suggestions from the LLM strategy."""
        return self.llm_strategy.refine(query)
    
    def to_string(self, tool_plan: ToolPlan) -> str:
        """Convert tool plan to string."""
        return tool_plan.model_dump_json()

    def execute_tools(self, tool_plan: ToolPlan) -> List[Dict[str, Any]]:
        """
        Execute tools recursively. First execute non-calculator tools,
        then use their responses to potentially invoke calculator tools.
        """
        responses = []
        has_multiple_plans = len(tool_plan.suggestions) > 1
        should_try_again:bool = False
        for suggestion in tool_plan.suggestions:
            has_depends_on = len(suggestion.depends_on) > 0
            if has_multiple_plans and has_depends_on and suggestion.tool == "calculator":
                should_try_again = True
                continue
            response = self._execute_single_tool(suggestion)
            responses.append(response)
        
        if should_try_again:
            new_tool_plan = self._evaluate_calculator_dependencies(responses)
            responses.extend(self.execute_tools(new_tool_plan))

        return responses
    
    def _evaluate_calculator_dependencies(self, responses: List[Dict[str, Any]]) -> ToolPlan:
        """Evaluate depends_on for calculator tools."""
        response_summary = "Based on these results: " + "; ".join(str(responses)) + ". What calculations should be performed?"
        tool_plan_for_calculators = self.get_tool_suggestions(response_summary)
        self.tool_plan.extend([suggestion.model_dump() for suggestion in tool_plan_for_calculators.suggestions])
        return tool_plan_for_calculators


    def _execute_single_tool(self, suggestion) -> Dict[str, Any]:
        """Execute a single tool and return the response."""
        try:
            self.tool_invoker.set_action(suggestion.tool)
            result = self.tool_invoker.execute(suggestion.args)

            return {
                "tool": suggestion.tool,
                "args": suggestion.args,
                "result": result,
                "success": True,
                "error": None
            }

        except Exception as e:
            return {
                "tool": suggestion.tool,
                "args": suggestion.args,
                "result": None,
                "success": False,
                "error": str(e)
            }

    def preprocess_query(self, query: str) -> str:
        """Hook method for preprocessing the query. Default: no preprocessing."""
        return query.strip().lower()

    def postprocess_responses(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hook method for post-processing tool responses. Default: no post-processing."""
        return responses



    def fuse_responses(self, responses: List[Dict[str, Any]], query: str) -> str:
        """
        Fuse tool responses into a final answer using an LLM, 
        with stricter formatting and validation.
        """
        # Build a text summary of tool responses
        response_text = "\n".join(
            f"- Response {i+1}: {str(r)}"
            for i, r in enumerate(responses) if r
        )

        answer = self.llm_strategy.query(f"""
            You are an agent tasked with fusing tool responses into a single final answer.
            
            Tools Used:
            {self.tool_plan}

            Tool Responses:
            {response_text}

            Original Query:
            {query}

            Formatting Rules:
            {FUSE_FORMAT_MESSAGE}
        """).strip()

        return answer



                                

        