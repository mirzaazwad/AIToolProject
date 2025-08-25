"""Tests for Calculator Tool"""

import pytest
from src.lib.tools.calculator import Calculator


@pytest.mark.usefixtures("calc")
class TestCalculator:
    """Test suite for Calculator tool."""

    @pytest.fixture(autouse=True)
    def calc(self):
        """Fixture that provides a Calculator instance for each test."""
        self.calc = Calculator()

    def test_addition(self):
        result = self.calc.execute({"expr": "1 + 1"})
        assert result == "2.0"

    def test_subtraction(self):
        result = self.calc.execute({"expr": "1 - 1"})
        assert result == "0.0"

    def test_multiplication(self):
        result = self.calc.execute({"expr": "2 * 2"})
        assert result == "4.0"

    def test_division(self):
        result = self.calc.execute({"expr": "4 / 2"})
        assert result == "2.0"

    def test_modulus(self):
        result = self.calc.execute({"expr": "5 % 2"})
        assert result == "1.0"

    def test_power(self):
        result = self.calc.execute({"expr": "2 ^ 3"})
        assert result == "8.0"

    def test_complex_expression(self):
        result = self.calc.execute({"expr": "1 + 2 * 3 - 4 / 2"})
        assert result == "5.0"

    def test_paranthesis_expression(self):
        result = self.calc.execute({"expr": "(1 + 2) * 3"})
        assert result == "9.0"

    def test_curly_bracket_expression(self):
        result = self.calc.execute({"expr": "1 + {(2 * 3) - 4}"})
        assert result == "3.0"

    def test_square_bracket_expression(self):
        result = self.calc.execute({"expr": "1 + ([{2 * (3 - 4)} - 2])"})
        assert result == "-3.0"

    def test_mixed_brackets_complex_1(self):
        result = self.calc.execute({"expr": "({[2 + 3 * (4 - 1)] + 5} * 2) - [3 ^ 2]"})
        assert result == "23.0"

    def test_mixed_brackets_complex_2(self):
        result = self.calc.execute({"expr": "[({2 + 3} * (4 + [5 - 2])) / {5}] + 7"})
        assert result == "14.0"

    def test_mixed_brackets_complex_3(self):
        result = self.calc.execute({"expr": "{[2 ^ (1 + 2)] % (5 - 2)} + (6 / [3])"})
        assert result == "4.0"

    def test_mixed_brackets_complex_4(self):
        result = self.calc.execute({"expr": "({[2 + 3] * (4 + 5)} - 6) / {7 - [8 % 3]}"})
        assert result == "7.8"
