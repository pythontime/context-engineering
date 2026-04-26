"""Extract Mermaid blocks from .md files and render them via @mermaid-js/mermaid-cli.

One-shot helper. Lives next to the diagrams it renders. Safe to delete or rerun.

Usage:
    python .render.py                # render everything
    python .render.py file.md        # render just that file's blocks
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

DIAGRAMS_DIR = Path(__file__).parent

# Map: source file -> list of (suffix, formats). suffix '' means no suffix.
# Renders are written next to the source.
PLAN: dict[str, list[tuple[str, list[str]]]] = {
    "system-overview.md": [("", ["svg"])],
    "azure-deploy.md": [("", ["svg"])],
    "langgraph-flow.md": [("", ["svg"])],
    "mcp-primitives.md": [("", ["svg"])],
    "graph-memory-architecture.md": [
        ("", ["svg"]),                    # block 1: system architecture
        ("-component-detail", ["svg"]),  # block 2: component details
        ("-data-flow", ["svg"]),          # block 3: data flow
    ],
    "schematica-system-overview.mmd": [("", ["svg", "png"])],
    "schematica-memory-architecture.mmd": [("", ["svg", "png"])],
    "schematica-langgraph-pipeline.mmd": [("", ["svg", "png"])],
    "scratchpad-architecture.mmd": [("", ["svg", "png"])],
}


MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


def extract_blocks(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8")
    if source.suffix == ".mmd":
        return [text]
    return MERMAID_BLOCK.findall(text)


def render_block(block: str, output: Path, fmt: str) -> bool:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".mmd", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(block)
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            "npx", "--yes", "@mermaid-js/mermaid-cli",
            "-i", str(tmp_path),
            "-o", str(output),
            "-b", "transparent",
        ]
        if fmt == "png":
            cmd.extend(["-w", "1600"])
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=(sys.platform == "win32")
        )
        if result.returncode != 0:
            print(f"  FAIL {output.name}")
            print(f"    stderr: {result.stderr[:300]}")
            return False
        print(f"  OK   {output.name}")
        return True
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else None
    items = (
        [(target, PLAN[target])] if target else list(PLAN.items())
    )

    failures = 0
    for filename, plan in items:
        source = DIAGRAMS_DIR / filename
        if not source.exists():
            print(f"SKIP {filename} (not found)")
            continue

        blocks = extract_blocks(source)
        print(f"\n{filename}: {len(blocks)} block(s)")

        if len(blocks) < len(plan):
            print(f"  WARN: plan expects {len(plan)} blocks, found {len(blocks)}")

        stem = source.stem
        for (suffix, formats), block in zip(plan, blocks):
            for fmt in formats:
                output = DIAGRAMS_DIR / f"{stem}{suffix}.{fmt}"
                if not render_block(block, output, fmt):
                    failures += 1

    print(f"\nDone. {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
