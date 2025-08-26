"""Schema for Tool Suggestion"""

import json
from typing import Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

ToolArgValue = Union[str, float, int]
ToolArgs = dict[str, ToolArgValue]
ToolSuggestionDict = dict[str, Union[str, ToolArgs, list[str]]]


class ToolArgument(BaseModel):
    """Base class for tool arguments."""

    model_config = ConfigDict(extra="allow")


class CalculatorArgs(ToolArgument):
    """Arguments for calculator tool."""

    expr: str = Field(..., description="Mathematical expression to evaluate")

    @field_validator("expr")
    @classmethod
    def validate_expr(cls, v):
        if not v or not v.strip():
            raise ValueError("Expression cannot be empty")
        return v.strip()


class WeatherArgs(ToolArgument):
    """Arguments for weather tool."""

    city: str = Field(..., description="City name for weather information")

    @field_validator("city")
    @classmethod
    def validate_city(cls, v):
        if not v or not v.strip():
            raise ValueError("City name cannot be empty")
        return v.strip()


class KnowledgeBaseArgs(ToolArgument):
    """Arguments for knowledge base tool."""

    query: str = Field(..., alias="q", description="Query for knowledge base search")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    model_config = ConfigDict(populate_by_name=True)


class CurrencyConverterArgs(ToolArgument):
    """Arguments for currency converter tool."""

    from_currency: str = Field(..., alias="from", description="Source currency code")
    to_currency: str = Field(..., alias="to", description="Target currency code")
    amount: float = Field(..., gt=0, description="Amount to convert")

    @field_validator("from_currency", "to_currency")
    @classmethod
    def validate_currency_code(cls, v):
        if not v or len(v.strip()) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        return v.strip().upper()

    model_config = ConfigDict(populate_by_name=True)


class ToolSuggestion(BaseModel):
    """Represents a single tool suggestion."""

    tool: str = Field(..., description="Name of the tool to execute")
    args: ToolArgs = Field(default_factory=dict, description="Arguments for the tool")
    depends_on: list[str] = Field(
        default_factory=list, description="List of tools that this tool depends on"
    )

    @field_validator("tool")
    @classmethod
    def validate_tool(cls, v):
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")

        valid_tools = {"calculator", "weather", "knowledge_base", "currency_converter"}
        if v not in valid_tools:
            raise ValueError(
                f"Unknown tool: {v}. Valid tools: {', '.join(valid_tools)}"
            )

        return v

    def to_dict(self) -> ToolSuggestionDict:
        """Convert to dictionary representation."""
        return {"tool": self.tool, "args": self.args, "depends_on": self.depends_on}

    @classmethod
    def from_dict(cls, data: ToolSuggestionDict) -> "ToolSuggestion":
        """Create ToolSuggestion from dictionary."""
        return cls(
            tool=data.get("tool", ""),
            args=data.get("args", {}),
            depends_on=data.get("depends_on", []),
        )


class ToolPlan(BaseModel):
    """Represents a plan with multiple tool suggestions."""

    suggestions: list[ToolSuggestion] = Field(
        default_factory=list, description="List of tool suggestions"
    )

    @field_validator("suggestions")
    @classmethod
    def validate_suggestions(cls, v):
        if not isinstance(v, list):
            raise ValueError("Suggestions must be a list")
        return v

    def to_dict(self) -> dict[str, list[ToolSuggestionDict]]:
        """Convert to dictionary representation."""
        return {
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions]
        }

    def to_list(self) -> list[ToolSuggestionDict]:
        """Convert to list representation (for backward compatibility)."""
        return [suggestion.to_dict() for suggestion in self.suggestions]

    @classmethod
    def from_list(cls, data: list[ToolSuggestionDict]) -> "ToolPlan":
        """Create ToolPlan from list of dictionaries."""
        suggestions = [ToolSuggestion.from_dict(item) for item in data]
        return cls(suggestions=suggestions)

    @classmethod
    def from_json_string(cls, json_str: str) -> "ToolPlan":
        """Create ToolPlan from JSON string."""
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return cls.from_list(data)
            elif isinstance(data, dict) and "suggestions" in data:
                return cls.from_list(data["suggestions"])
            else:
                raise ValueError("Invalid JSON structure for ToolPlan")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

    def __len__(self) -> int:
        """Return number of suggestions."""
        return len(self.suggestions)

    def __iter__(self) -> iter:
        """Make ToolPlan iterable."""
        return iter(self.suggestions)

    def __getitem__(self, index: int) -> ToolSuggestion:
        """Allow indexing into suggestions."""
        return self.suggestions[index]


def create_calculator_suggestion(expression: str) -> ToolSuggestion:
    """Create a calculator tool suggestion."""
    args = CalculatorArgs(expr=expression)
    return ToolSuggestion(tool="calculator", args=args.model_dump())


def create_weather_suggestion(city: str) -> ToolSuggestion:
    """Create a weather tool suggestion."""
    args = WeatherArgs(city=city)
    return ToolSuggestion(tool="weather", args=args.model_dump())


def create_knowledge_base_suggestion(query: str) -> ToolSuggestion:
    """Create a knowledge base tool suggestion."""
    args = KnowledgeBaseArgs(query=query)
    return ToolSuggestion(tool="knowledge_base", args=args.model_dump())


def create_currency_converter_suggestion(
    from_currency: str, to_currency: str, amount: float
) -> ToolSuggestion:
    """Create a currency converter tool suggestion."""
    args = CurrencyConverterArgs(
        from_currency=from_currency, to_currency=to_currency, amount=amount
    )
    return ToolSuggestion(tool="currency_converter", args=args.model_dump())
