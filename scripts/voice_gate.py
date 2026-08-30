#!/usr/bin/env python3
"""
voice_gate.py — the blocking language gate.

Reads voice_gate_wordlist.json (same folder) and checks a draft for AI-slop
language, optional spelling-variant slips, and anything you've added yourself.

Why bother: readers pattern-match AI writing fast, and trust drops sharply the
moment they suspect it. The gate catches the obvious tells so you can spend your
attention on the writing that matters.

Usage:
  python3 voice_gate.py <draft.md>
  python3 voice_gate.py --file <draft.md> --spelling au
  echo "some copy" | python3 voice_gate.py

  --spelling au   flag US spellings (you write in UK/AU English)
  --spelling us   flag UK/AU spellings (you write in US English)
  --spelling off  ignore spelling entirely  [default]

Exit codes: 0 = clean (WARNs are allowed) · 1 = at least one ERROR.

Importable:  from voice_gate import check_text
             check_text(text, spelling="au") -> list of violation dicts
"""

import argparse
import json
import re
import sys
from pathlib import Path

WORDLIST_PATH = Path(__file__).with_name("voice_gate_wordlist.json")


def load_rules():
    if not WORDLIST_PATH.exists():
        sys.exit(f"wordlist missing: {WORDLIST_PATH} — the gate fails closed, restore it first")
    return json.loads(WORDLIST_PATH.read_text())["rules"]


def strip_notes(text: str) -> str:
    """Drop a trailing 'NOTES TO SELF' block so we lint the copy, not the reminders."""
    m = re.search(r"^#{1,3}\s*NOTES (TO SELF|FOR ME)", text, re.M | re.I)
    return text[: m.start()] if m else text


def check_text(text: str, spelling: str = "off") -> list[dict]:
    text = strip_notes(text)
    violations = []
    for rule in load_rules():
        want = rule.get("spelling")
        if want and want != spelling:
            continue  # spelling rule that doesn't apply to the chosen variant
        for m in re.finditer(rule["pattern"], text, re.IGNORECASE):
            ctx = text[max(0, m.start() - 30) : m.end() + 30].replace("\n", " ").strip()
            violations.append(
                {
                    "severity": rule["severity"],
                    "category": rule["category"],
                    "hit": m.group(0),
                    "context": ctx,
                    "why": rule.get("why", ""),
                }
            )
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="draft file (or use --file, or pipe stdin)")
    ap.add_argument("--file")
    ap.add_argument("--spelling", choices=["au", "us", "off"], default="off")
    a = ap.parse_args()

    src = a.file or a.path
    if src:
        p = Path(src)
        if not p.exists():
            sys.exit(f"file not found: {p}")
        text = p.read_text()
        label = str(p)
    else:
        if sys.stdin.isatty():
            sys.exit("usage: voice_gate.py <draft.md>   (or pipe text in)")
        text = sys.stdin.read()
        label = "(stdin)"

    v = check_text(text, spelling=a.spelling)
    errors = [x for x in v if x["severity"] == "ERROR"]
    warns = [x for x in v if x["severity"] == "WARN"]

    if not v:
        print(f"✓ gate clean — {label}")
        return 0

    for x in errors:
        print(f"ERROR  [{x['category']}]  '{x['hit']}'")
        print(f"       …{x['context']}…")
        if x["why"]:
            print(f"       why: {x['why']}")
    for x in warns:
        print(f"warn   [{x['category']}]  '{x['hit']}'")
        print(f"       …{x['context']}…")

    print()
    print(f"{len(errors)} error(s), {len(warns)} warning(s) — {label}")
    if errors:
        print("Rewrite every ERROR line, then run the gate again. Don't bypass it.")
        return 1
    print("Warnings only — read them, then judge. Nothing is blocking.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
