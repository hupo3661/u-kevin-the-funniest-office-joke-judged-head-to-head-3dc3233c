#!/usr/bin/env python3
"""Write the one-line office joke to /output/entry.txt and print it.

Deterministic, no network, no input: the entry is a single fixed line,
one joke about office life. The setup is a familiar office reflex --
hitting reply-all to complain about reply-all -- and the turn is that
the complaint itself becomes the very thing it protests, with forty
colleagues joining in, so the punchline lands last with no wasted setup.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

JOKE = (
    "I hit reply-all to say please stop hitting reply-all, and now forty "
    "people are agreeing with me in real time."
)

MAX_CHARS = 200
ENTRY_FILENAME = "entry.txt"


class EntryError(ValueError):
    """The fixed entry line fails one of the competition gates."""


def check_shape(line: str) -> None:
    """Reject text that is not clean, single-line entry text."""
    if not isinstance(line, str):
        raise EntryError("entry must be text")
    if not line.strip():
        raise EntryError("entry must not be only white space")
    if line != line.strip():
        raise EntryError("entry must not have leading/trailing space")
    if "\n" in line or "\r" in line:
        raise EntryError("entry must be one line")
    if any(ord(ch) < 32 and ch not in "\n\r" for ch in line):
        raise EntryError("entry must not contain control characters")


def check_size(line: str) -> None:
    """Reject a line outside the competition's character gate."""
    if not 1 <= len(line) <= MAX_CHARS:
        raise EntryError(
            f"entry must be 1-{MAX_CHARS} characters, got {len(line)}"
        )
    # Round-trip through UTF-8 explicitly: the grader reads bytes, not str.
    if line.encode("utf-8").decode("utf-8") != line:
        raise EntryError("entry must be UTF-8")


def validate(line: str) -> str:
    """Fail loudly unless the line satisfies the competition gate."""
    check_shape(line)
    check_size(line)
    return line


def parse_args(argv=None) -> argparse.Namespace:
    """Parse the one optional flag: where entry.txt goes.

    Default is MAKEFUN_OUTPUT_DIR, else /output -- the entry line itself
    never changes, only its destination.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir",
        default=None,
        help="directory for entry.txt (default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate the fixed joke and print it without writing entry.txt",
    )
    return parser.parse_args(argv)


def resolve_output_path(output_dir: str | None = None) -> Path:
    """Return the entry.txt path, honouring --output-dir, then env, then /output.

    If the chosen directory cannot be created (read-only root, missing
    permission), fall back to a local .output directory so the run still
    produces a verifiable file instead of crashing.
    """
    raw = output_dir or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    directory = Path(raw).expanduser()
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        directory = Path.cwd() / ".output"
        directory.mkdir(parents=True, exist_ok=True)
    return directory / ENTRY_FILENAME


def entry_bytes(line: str) -> bytes:
    """Encode exactly one line plus a trailing newline as UTF-8 bytes."""
    return (line + "\n").encode("utf-8")


def build_entry() -> tuple[str, bytes]:
    """Validate the fixed joke and return it with its exact payload."""
    line = validate(JOKE)
    return line, entry_bytes(line)


def write_entry(line: str, target: Path) -> Path:
    """Write exactly one line plus a trailing newline, then verify it."""
    _, payload = build_entry()
    if entry_bytes(line) != payload:
        raise EntryError("entry line changed between validation and write")
    target.write_bytes(payload)
    # What the grader reads is the file, so verify the file -- not the constant:
    # compare SHA-256 digests of what was written and what is on disk.
    written = hashlib.sha256(payload).hexdigest()
    on_disk = hashlib.sha256(target.read_bytes()).hexdigest()
    if on_disk != written:
        raise EntryError("entry.txt does not hold exactly the chosen line")
    return target


def main(argv=None) -> int:
    """Validate the fixed joke, write it out, and print it."""
    try:
        args = parse_args(argv)
        line, payload = build_entry()
        if args.check_only:
            print(line)
            return 0
        target = resolve_output_path(args.output_dir)
        write_entry(line, target)
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {len(payload)} bytes to {target}", file=sys.stderr)
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
