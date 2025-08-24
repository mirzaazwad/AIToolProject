"""
StubLLMStrategy Implementation
Handles Calculator, Weather, KnowledgeBase, CurrencyConverter.
"""

import re
import math
from typing import Optional
from src.data.schemas.tools.tool import (
    CalculatorArgs,
    WeatherArgs,
    KnowledgeBaseArgs,
    CurrencyConverterArgs,
    ToolPlan,
    ToolSuggestion,
)
from src.lib.llm.base import LLMStrategy
from tests.constants.weather import CITY_TEMPERATURE
from tests.constants.calculator import OPERATOR_PATTERNS


def safe_eval(expr: str) -> Optional[float]:
    try:
        return eval(expr, {"__builtins__": {}}, {"sqrt": math.sqrt, "pow": pow})
    except Exception:
        return None


def extract_expression(prompt: str) -> Optional[str]:
    """
    Extract a numeric expression from a prompt string.
    Ignores any words/characters before the numbers/operators.
    Handles:
    - Percentages: "12.5% of 243"
    - Powers: "2 ^ 3"
    - Basic arithmetic: "1 + 1"
    - 'add X and Y' / 'add X to Y'
    """
    cleaned_prompt = re.sub(
        r"^(?:what is|calculate|compute|please|find|the result of)\s*",
        "",
        prompt,
        flags=re.IGNORECASE,
    ).strip()

    for pat in OPERATOR_PATTERNS:
        m = pat.search(cleaned_prompt)
        if m:
            if "%" in m.group(0):
                return f"({m.group(1)} / 100) * {m.group(2)}"
            if "^" in m.group(0):
                return f"{m.group(1)}**{m.group(2)}"

    m = re.search(r"([0-9\s\+\-\*/\.%\(\)]+)", cleaned_prompt)
    if m:
        return m.group(1).strip()

    m = re.search(
        r"add\s+([0-9]+(?:\.[0-9]+)?)\s+(?:and|to)\s+([0-9]+(?:\.[0-9]+)?)",
        cleaned_prompt,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(1)} + {m.group(2)}"

    return None


def extract_cities(prompt: str) -> list[str]:
    cities = []
    for city in CITY_TEMPERATURE:
        if city in prompt.lower():
            cities.append(city)
    return cities


def extract_knowledge_base_query(prompt: str) -> Optional[str]:
    pat = re.compile(
        r"(?:who\s+is|tell\s+me\s+about|what\s+is)\s+([A-Za-z\s]+?)[\?\.!]*$",
        re.IGNORECASE,
    )
    m = pat.search(prompt.strip())
    if m:
        return m.group(1).strip().lower()
    return None


def extract_currency_conversion(prompt: str):
    m = re.search(
        r"average of (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?) (USD|EUR) into (USD|EUR)",
        prompt,
        re.IGNORECASE,
    )
    if m:
        return (
            m.group(3).upper(),
            m.group(4).upper(),
            (float(m.group(1)) + float(m.group(2))) / 2,
        )
    m = re.search(
        r"convert (\d+(?:\.\d+)?) (USD|EUR) to (USD|EUR)", prompt, re.IGNORECASE
    )
    if m:
        return (m.group(2).upper(), m.group(3).upper(), float(m.group(1)))

    return None


class StubLLMStrategy(LLMStrategy):
    def query(self, prompt: str) -> str:
        pass

    def refine(self, prompt: str) -> ToolPlan:
        cities = extract_cities(prompt)
        expr = extract_expression(prompt)
        q = extract_knowledge_base_query(prompt)
        suggestions = []
        if expr:
            expr = expr.strip()
            if expr:
                suggestions.append(
                    ToolSuggestion(
                        tool="calculator", args=CalculatorArgs(expr=expr).model_dump()
                    )
                )
                cities = extract_cities(prompt)
        if cities:
            for c in cities:
                suggestions.append(
                    ToolSuggestion(
                        tool="weather", args=WeatherArgs(city=c.title()).model_dump()
                    )
                )
        if q:
            suggestions.append(
                ToolSuggestion(
                    tool="knowledge_base", args=KnowledgeBaseArgs(query=q).model_dump()
                )
            )

        m_avg_add = re.search(
            r"add\s+([0-9]+(?:\.[0-9]+)?)\s+to\s+the\s+average\s+(?:temperature\s+)?(?:in\s+)?([A-Za-z]+)\s*(?:and|,)\s*([A-Za-z]+)",
            prompt,
            re.IGNORECASE,
        )
        if m_avg_add:
            add_val, c1, c2 = m_avg_add.groups()
            expr = f"({c1}_temp + {c2}_temp) / 2 + {add_val}"
            calc_args = CalculatorArgs(expr=expr).model_dump()
            suggestions.append(
                ToolSuggestion(
                    tool="calculator", args=calc_args, depends_on=["weather"]
                )
            )

        cur = extract_currency_conversion(prompt)
        if cur:
            src, tgt, amount = cur
            suggestions.append(
                ToolSuggestion(
                    tool="currency_converter",
                    args=CurrencyConverterArgs(
                        from_currency=src, to_currency=tgt, amount=amount
                    ).model_dump(by_alias=True),
                )
            )

        return ToolPlan(suggestions=suggestions)
