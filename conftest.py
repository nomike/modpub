"""Pytest configuration to ensure modpub package can be imported during tests."""

import sys
from pathlib import Path

# Add the project root directory to Python path so tests can import modpub
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))