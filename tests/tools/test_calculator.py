"""Tests for Calculator Tool"""
from src.lib.tools.calculator import Calculator

def test_addition():
    calc = Calculator()
    result = calc.execute({"expr": "1 + 1"})
    assert result == "2.0"

def test_subtraction():
    calc = Calculator()
    result = calc.execute({"expr": "1 - 1"})
    assert result == "0.0"


def test_multiplication():
    calc = Calculator()
    result = calc.execute({"expr": "2 * 2"})
    assert result == "4.0"


def test_division():
    calc = Calculator()
    result = calc.execute({"expr": "4 / 2"})
    assert result == "2.0"


def test_modulus():
    calc = Calculator()
    result = calc.execute({"expr": "5 % 2"})
    assert result == "1.0"

def test_power():
    calc = Calculator()
    result = calc.execute({"expr": "2 ^ 3"})
    assert result == "8.0"

def test_complex_expression():
    calc = Calculator()
    result = calc.execute({"expr": "1 + 2 * 3 - 4 / 2"})
    assert result == "5.0"

def test_paranthesis_expression():
    calc = Calculator()
    result = calc.execute({"expr": "(1 + 2) * 3"})
    assert result == "9.0"

def test_curly_bracket_expression():
    calc = Calculator()
    result = calc.execute({"expr": "1 + {(2 * 3) - 4}"})
    assert result == "3.0"

def test_square_bracket_expression():
    calc = Calculator()
    result = calc.execute({"expr": "1 + ([{2 * (3 - 4)} - 2])"})
    assert result == "-3.0"


def test_mixed_brackets_complex_1():
    calc = Calculator()
    result = calc.execute({"expr": "({[2 + 3 * (4 - 1)] + 5} * 2) - [3 ^ 2]"})
    assert result == "23.0"

def test_mixed_brackets_complex_2():
    calc = Calculator()
    result = calc.execute({"expr": "[({2 + 3} * (4 + [5 - 2])) / {5}] + 7"})
    assert result == "14.0"

def test_mixed_brackets_complex_3():
    calc = Calculator()
    result = calc.execute({"expr": "{[2 ^ (1 + 2)] % (5 - 2)} + (6 / [3])"})
    assert result == "4.0"
