#!/usr/bin/env python3
"""Write the one-line office joke to /output/entry.txt and print it.

Deterministic, no network, no input: the entry is a single fixed line,
one joke about office life. The setup is a familiar office reflex --
hitting reply-all to complain about reply-all -- and the turn is that
the complaint itself becomes the very thing it protests, with forty
colleagues joining in, so the punchline lands last with no wasted setup.
"""

import os
from pathlib import Path

JOKE = (
    "I hit reply-all to say please stop hitting reply-all, and now forty "
    "people are agreeing with me in real time."
)

MAX_CHARS = 200


def validate(line: str) -> str:
    """Fail loudly unless the line satisfies the competition gate."""
    assert isinstance(line, str), "entry must be text"
    assert line == line.strip(), "entry must not have leading/trailing space"
    assert line.strip(), "entry must not be only white space"
    assert "\n" not in line and "\r" not in line, "entry must be one line"
    assert 1 <= len(line) <= MAX_CHARS, (
        f"entry must be 1-{MAX_CHARS} characters, got {len(line)}"
    )
    # Round-trip through UTF-8 explicitly: the grader reads bytes, not str.
    assert line.encode("utf-8").decode("utf-8") == line, "entry must be UTF-8"
    return line


def resolve_output_path() -> Path:
    """Return the entry.txt path, honouring MAKEFUN_OUTPUT_DIR if set."""
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "entry.txt"


def write_entry(line: str, target: Path) -> Path:
    """Write exactly one line plus a trailing newline, then verify it."""
    target.write_text(line + "\n", encoding="utf-8")
    # What the grader reads is the file, so verify the file -- not the constant.
    assert target.read_text(encoding="utf-8") == line + "\n", (
        "entry.txt does not hold exactly the chosen line"
    )
    return target


def main() -> None:
    line = validate(JOKE)
    write_entry(line, resolve_output_path())
    print(line)


if __name__ == "__main__":
    main()
