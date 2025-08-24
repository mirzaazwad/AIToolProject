"""
Pytest configuration file.
This file is automatically loaded by pytest and sets up the test environment.
"""

import sys
import os
from pathlib import Path


project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = f"{project_root}:{os.environ['PYTHONPATH']}"
else:
    os.environ['PYTHONPATH'] = str(project_root)
