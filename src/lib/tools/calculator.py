"""Calculator Tool"""

from .base import Action
from ..errors.tools.calculator import (
    ExpressionError,
    TokenizationError,
    EvaluationError,
    BracketMismatchError,
)


class Calculator(Action):
    """Calculator tool using Shunting Yard algorithm."""

    def execute(self, args: dict) -> str:
        expr = args.get("expr")
        if not expr:
            raise ExpressionError("No expression provided")

        if not isinstance(expr, str):
            raise ExpressionError("Expression must be a string")

        if not expr.strip():
            raise ExpressionError("Expression cannot be empty")

        tokens = self._tokenize(expr)
        postfix = self._to_postfix(tokens)
        result = self._eval_postfix(postfix)
        return str(result)

    def _tokenize(self, expr: str) -> list[str]:
        """Tokenize mathematical expression into numbers and operators."""
        tokens = []
        num = ""
        for ch in expr:
            if ch.isdigit() or ch == ".":
                num += ch
            else:
                if num:
                    tokens.append(num)
                    num = ""
                if ch in "+-*/%^(){}[]":
                    tokens.append(ch)
                elif ch.isspace():
                    continue
                else:
                    raise TokenizationError(f"Invalid character: '{ch}'")
        if num:
            tokens.append(num)
        return tokens


    def _is_number(self, token: str) -> bool:
        """Check if token is a valid number (int or float)."""
        return token.replace(".", "", 1).isdigit()

    def _apply_operator(self, a: float, b: float, op: str) -> float:
        """Apply an operator on two operands."""
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise EvaluationError("Division by zero")
            return a / b
        if op == "%":
            if b == 0:
                raise EvaluationError("Modulo by zero")
            return a % b
        if op == "^":
            return a**b
        raise EvaluationError(f"Unknown operator: '{op}'")

    def _handle_operator(self, token: str, stack: list[str], output: list[str], precedence: dict):
        """Handle operator tokens according to precedence rules."""
        while stack and stack[-1] in precedence and precedence[stack[-1]] >= precedence[token]:
            output.append(stack.pop())
        stack.append(token)

    def _handle_closing_bracket(self, token: str, stack: list[str], output: list[str], closing: dict):
        """Handle closing bracket by unwinding stack until matching opening bracket."""
        while stack and stack[-1] != closing[token]:
            output.append(stack.pop())
        if not stack:
            raise BracketMismatchError("Mismatched closing bracket")
        stack.pop()


    def _to_postfix(self, tokens: list[str]) -> list[str]:
        """Convert infix tokens to postfix notation using Shunting Yard algorithm."""
        output = []
        stack = []

        precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
        opening = {"(": ")", "{": "}", "[": "]"}
        closing = {")": "(", "}": "{", "]": "["}

        for token in tokens:
            if self._is_number(token):
                output.append(token)
            elif token in precedence:
                self._handle_operator(token, stack, output, precedence)
            elif token in opening:
                stack.append(token)
            elif token in closing:
                self._handle_closing_bracket(token, stack, output, closing)
            else:
                raise TokenizationError(f"Unknown token: '{token}'")

        while stack:
            if stack[-1] in opening:
                raise BracketMismatchError("Unclosed opening bracket")
            output.append(stack.pop())

        return output

    def _eval_postfix(self, postfix: list[str]) -> float:
        """Evaluate postfix expression and return the result."""
        stack = []
        for token in postfix:
            if self._is_number(token):
                try:
                    stack.append(float(token))
                except ValueError:
                    raise EvaluationError(f"Invalid number: '{token}'")
            else:
                if len(stack) < 2:
                    raise EvaluationError("Insufficient operands for operation")

                b = stack.pop()
                a = stack.pop()
                stack.append(self._apply_operator(a, b, token))

        if len(stack) != 1:
            raise EvaluationError("Invalid expression: multiple results")

        return stack[0]
