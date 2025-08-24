"""AgentStub that utilizes the StubToolInvoker/StubLLMStrategy"""

from typing import List, Dict, Any
from src.lib.agents.base import Agent
from .llm import StubLLMStrategy
from .tools.invoker import StubToolInvoker
from src.constants.messages import FAILED_AGENT_MESSAGE
import re


class AgentStub(Agent):
    """Test-oriented Agent that resolves simple calculator dependencies using stub outputs."""

    def __init__(self):
        super().__init__(llm_strategy=StubLLMStrategy(), tool_invoker=StubToolInvoker())

    @staticmethod
    def _extract_first_number(s: str) -> float | None:
        """Extract the first numeric value (int/float) from a string."""
        if not s or not isinstance(s, str):
            return None
        match = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:°\s*C|°C|C|F)?", s)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def _execute_single_tool(self, suggestion) -> Dict[str, Any]:
        """Execute a single tool and return a standardized response."""
        tool_name = getattr(suggestion, "tool", None) or getattr(
            suggestion, "tool_name", None
        )
        if not tool_name:
            return {"tool": None, "args": {}, "success": False, "result": None}

        args = getattr(suggestion, "args", {}) or {}
        self.tool_invoker.set_action(tool_name)

        try:
            result = self.tool_invoker.execute(args)
            return {"tool": tool_name, "args": args, "success": True, "result": result}
        except Exception as e:
            result = None

        return {
            "tool": tool_name,
            "args": args,
            "success": False,
            "result": self._fallback_result(tool_name, args),
        }

    @staticmethod
    def _fallback_result(tool_name: str, args: dict) -> str:
        """Generate fallback response if a tool fails or returns None."""
        if tool_name == "calculator":
            return "0"
        if tool_name == "weather":
            city = args.get("city", "Unknown")
            return f"Weather in {city}: 18.0°C, clear sky"
        if tool_name == "knowledge_base":
            query = args.get("query", "Unknown")
            return f"Result for query: {query}"
        return "OK"

    def execute_tools(self, tool_plan) -> List[Dict[str, Any]]:
        """
        Execute tools in two passes:
         1. Execute non-dependent tools immediately.
         2. Resolve calculator dependencies using extracted context.
         3. Re-run if dependencies remain.
        """
        responses, deferred_calcs = self._run_initial_tools(tool_plan)
        context = self._build_weather_context(responses)

        executed_calcs = self._run_calculators(deferred_calcs, context, responses)
        responses.extend(executed_calcs)
        return responses

    def _run_initial_tools(self, tool_plan):
        """Run tools that don't have dependencies and collect deferred calculators."""
        responses, deferred_calcs = [], []
        for suggestion in tool_plan.suggestions:
            is_calc = suggestion.tool == "calculator"
            has_deps = bool(getattr(suggestion, "depends_on", []) or [])
            if is_calc and has_deps:
                deferred_calcs.append(suggestion)
            else:
                responses.append(self._execute_single_tool(suggestion))
        return responses, deferred_calcs

    def _build_weather_context(self, responses):
        """Extract weather data to a lookup dict for calculators."""
        context = {}
        for r in responses:
            if r.get("tool") != "weather" or not r.get("success"):
                continue
            result = r.get("result")
            city = self._extract_city(r) or None
            if city:
                temp = self._extract_first_number(str(result))
                if temp is not None:
                    key_base = city.strip()
                    context[f"{key_base.lower()}_temp"] = temp
                    context[f"{key_base.title()}_temp"] = temp
        return context

    @staticmethod
    def _extract_city(response) -> str | None:
        """Extract city name from response args or result string."""
        args = response.get("args") or {}
        if isinstance(args, dict) and args.get("city"):
            return args.get("city")

        result_str = response.get("result")
        if isinstance(result_str, str):
            match = re.search(
                r"Weather\s+in\s+([A-Za-z\s]+):", result_str, re.IGNORECASE
            )
            if match:
                return match.group(1).strip()
        return None

    def _run_calculators(self, calculators, context, existing_responses):
        """Substitute context values into calculator expressions and execute."""
        executed, deferred = [], []
        for calc in calculators:
            expr = self._substitute_context(calc.args.get("expr", ""), context)
            if re.search(r"[A-Za-z_]+_temp", expr):
                deferred.append(calc)
                continue
            calc.args = {"expr": expr}
            executed.append(self._execute_single_tool(calc))

        if deferred:
            new_plan = self._evaluate_calculator_dependencies(
                existing_responses + executed
            )
            if new_plan and getattr(new_plan, "suggestions", []):
                executed.extend(self.execute_tools(new_plan))
        return executed

    @staticmethod
    def _substitute_context(expr: str, context: dict) -> str:
        """Replace placeholders in a calculator expression with numeric values."""
        expr = str(expr)
        for placeholder, value in context.items():
            expr = re.sub(
                rf"\b{re.escape(placeholder)}\b", str(value), expr, flags=re.IGNORECASE
            )
        return expr

    def fuse_responses(self, responses: List[Dict[str, Any]], query: str) -> str:
        """Combine tool responses into a final answer."""
        try:
            if not responses:
                return "No valid responses from tools."

            successful = [r for r in responses if r.get("success")]
            if not successful:
                return "No valid responses from tools."

            calculator_response = self._get_last_calculator_result(successful, query)
            if calculator_response:
                return calculator_response

            weather_response = self._get_weather_responses(successful, query)
            if weather_response:
                return weather_response

            knowledge_base_response = self._get_knowledge_responses(successful)
            if knowledge_base_response:
                return knowledge_base_response

            return self._format_generic_responses(successful)

        except Exception:
            return FAILED_AGENT_MESSAGE

    def _get_last_calculator_result(self, responses, query):
        calc_results = [
            r
            for r in responses
            if r.get("tool") == "calculator" and r.get("result") is not None
        ]
        if not calc_results:
            return None
        val = str(calc_results[-1]["result"])
        if any(
            k in query.lower() for k in ["temperature", "weather"]
        ) and not val.endswith("°C"):
            val = f"{val}°C"
        return val

    @staticmethod
    def _get_weather_responses(responses, query):
        weather_results = [r for r in responses if r.get("tool") == "weather"]
        if not weather_results:
            return None
        formatted = []
        for r in weather_results:
            args, res = r.get("args", {}), r.get("result")
            city = args.get("city") if isinstance(args, dict) else None
            formatted.append(AgentStub._format_weather_response(city, res, query))
        return "; ".join(formatted)

    @staticmethod
    def _format_weather_response(city, res, query):
        if not city:
            return str(res)
        q = query.lower()
        if isinstance(res, dict):
            if "summary" in q or "weather" in q or "summarize" in q:
                return res.get("description", str(res))
            if "temperature" in q:
                return f"{res.get('temp_c', '?')}°C"
            if "humidity" in q:
                return f"{res.get('humidity', '?')}%"
            if "wind" in q:
                return f"{res.get('wind_speed', '?')} m/s"
        return f"{str(city).title()}: {str(res)}"

    @staticmethod
    def _get_knowledge_responses(responses):
        kb_results = [r for r in responses if r.get("tool") == "knowledge_base"]
        if kb_results:
            return kb_results[0]["result"].summary
        return None

    @staticmethod
    def _format_generic_responses(responses):
        results = [
            str(r.get("result")) for r in responses if r.get("result") is not None
        ]
        if not results:
            return "No valid responses from tools."
        return (
            results[0]
            if len(results) == 1
            else "\n".join(f"- {i+1}: {s}" for i, s in enumerate(results))
        )
