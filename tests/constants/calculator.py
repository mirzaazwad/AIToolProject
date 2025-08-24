"""Constants for Calculator testing"""
import re

OPERATOR_PATTERNS = [
    re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*of\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
    re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*\^\s*([0-9]+(?:\.[0-9]+)?)"),
]