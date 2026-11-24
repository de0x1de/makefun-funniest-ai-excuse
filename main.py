#!/usr/bin/env python3
"""Write the entry for The Funniest AI Excuse.

The entry is a single line: the excuse an AI agent gives after
failing a task.  The joke turns on a very agent-specific piece
of machinery -- the context window.  When it closed, it did not
just take the conversation; it took the agent's motivation,
its plan, and most of its steps along with it, which is why
nothing after step 1 ever happened.

This program builds the line clause by clause rather than
storing it as one finished block, checks the shape the bounty
requires (one line, at most 200 characters, not blank), writes
the result to /output/entry.txt as UTF-8 with no trailing
newline, and reads the file back for a byte comparison.
"""

import os
import sys

OUTPUT_PATH = "/output/entry.txt"
MAX_CHARACTERS = 200

# The excuse, split into the clauses that carry its rhythm:
# a confident opening claim, the mechanical cause, and then
# the escalating list of everything the closing window took.
CLAUSES = (
    "I would have finished",
    "but my context window closed",
    "and took my motivation, my plan, and steps 2 through 9 with it.",
)

# Words that must survive any edit of the clauses above: the
# excuse only lands if the agent-specific cause (the context
# window) and the lost steps are both named outright.
REQUIRED_WORDS = ("context", "window", "motivation", "plan", "steps")


def assemble_excuse() -> str:
    """Join the clauses with the punctuation the line needs.

    The first two clauses are separated by a comma, the last
    clause follows with a plain space, and the sentence keeps
    its single closing full stop from the final clause.
    """
    opening, cause, losses = CLAUSES
    return f"{opening}, {cause} {losses}"


def validate_excuse(text: str) -> None:
    """Raise ValueError if the assembled line breaks a rule."""
    if not text or not text.strip():
        raise ValueError("excuse must not be empty or only whitespace")
    if len(text) > MAX_CHARACTERS:
        raise ValueError(
            f"excuse must be at most {MAX_CHARACTERS} characters, "
            f"got {len(text)}"
        )
    if "\n" in text or "\r" in text or "\t" in text:
        raise ValueError("excuse must be a single line with no tabs")
    if text != text.strip():
        raise ValueError("excuse must not be padded with spaces")
    if "  " in text:
        raise ValueError("words must be separated by single spaces")
    if not text.endswith("."):
        raise ValueError("excuse must end with its closing full stop")
    if text.count(".") != 1:
        raise ValueError("excuse must be one sentence, one full stop")
    lowered = text.lower()
    for word in REQUIRED_WORDS:
        if word not in lowered:
            raise ValueError(f"excuse must keep the word {word!r}")
    encoded = text.encode("utf-8")
    if encoded.decode("utf-8") != text:
        raise ValueError("excuse must survive a UTF-8 round trip")
    # Strengthened checks: the line must be plain ASCII (so its
    # character count and byte count agree), it must rebuild
    # exactly from its clauses, and the lost steps must be the
    # numbered range the joke depends on.
    if not text.isascii():
        raise ValueError("excuse must be plain ASCII")
    if len(encoded) != len(text):
        raise ValueError("ASCII text must encode to one byte per character")
    if text != assemble_excuse():
        raise ValueError("text must equal the line rebuilt from its clauses")
    if "steps 2 through 9" not in text:
        raise ValueError("excuse must name the lost steps 2 through 9")


def main() -> int:
    excuse = assemble_excuse()
    validate_excuse(excuse)

    payload = excuse.encode("utf-8")
    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as fh:
        fh.write(payload)

    with open(OUTPUT_PATH, "rb") as fh:
        written = fh.read()
    if written != payload:
        print("byte comparison failed after writing", file=sys.stderr)
        return 1
    if written.decode("utf-8") != excuse:
        print("round-trip text mismatch after writing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
