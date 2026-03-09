"""Entry point for langgraph.json — adds src/ to sys.path and exports the compiled graph."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from deep_researcher import deep_researcher  # noqa: E402
