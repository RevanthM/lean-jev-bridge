"""Reject proof holes and explicit axioms in project Lean source."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
for path in [root / "Bridge.lean", root / "Main.lean", *sorted((root / "Bridge").glob("*.lean"))]:
    text = path.read_text()
    # Strip ordinary comments before matching identifiers.
    text = re.sub(r"/\-.*?\-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    if re.search(r"\b(sorry|admit|axiom)\b", text):
        raise SystemExit(f"Unsupported proof declaration: {path.relative_to(root)}")
print("Project Lean sources contain no proof holes or explicit axioms.")
