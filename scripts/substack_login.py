#!/usr/bin/env python3
"""
substack_login.py — the ONE-TIME login for Path B.

You log in yourself, by hand, in a browser window this script opens. The session
is saved to a browser profile folder inside this skill, and substack_draft.py
reuses it from then on. You never hand your password to a script.

Why manual: automating Substack's email+password login tends to land you as a
READER, not the author of your publication — you then hit a "this page is
private" wall on your own editor. Logging in the normal way (magic link, Google,
whatever you actually use) avoids that entirely.

Run:
  python3 substack_login.py

Needs: pip install playwright && python3 -m playwright install chromium
Reads SUBSTACK_PUBLICATION from ../.env (e.g. yourname.substack.com).
"""

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = SKILL_DIR / ".chrome-profile"
ENV_PATH = SKILL_DIR / ".env"


def read_pub() -> str:
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("SUBSTACK_PUBLICATION="):
                pub = line.partition("=")[2].strip()
                if pub and "yourname" not in pub:
                    return pub
    sys.exit(
        f"Set SUBSTACK_PUBLICATION in {ENV_PATH} first.\n"
        "It's your publication's subdomain, e.g. yourname.substack.com\n"
        "(copy .env.example to .env if you haven't yet)"
    )


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "Playwright isn't installed. Either:\n"
            "  pip install playwright && python3 -m playwright install chromium\n"
            "…or just use Path A (the copy page) — it needs none of this."
        )

    pub = read_pub()
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR), headless=False, slow_mo=10
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://substack.com/sign-in", wait_until="domcontentloaded")

        print("\n" + "=" * 68)
        print("A browser window is open at the Substack sign-in page.")
        print("→ Log in the way you NORMALLY do (magic link / Google / password).")
        print(f"→ Make sure you land in {pub} as the AUTHOR —")
        print("  you should be able to see your Dashboard and a 'New post' button.")
        print("→ Then come back here and press ENTER to save the session.")
        print("=" * 68 + "\n")

        try:
            input("Press ENTER once you're logged in as the author… ")
        except EOFError:
            page.wait_for_timeout(90000)

        page.goto(f"https://{pub}/publish/post", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        blocked = page.get_by_text(
            re.compile(r"this page is private|sign in to", re.I)
        ).first.is_visible(timeout=2500)

        if blocked:
            print("⚠ Still hitting the private-page wall — that login isn't the author.")
            print("  Check SUBSTACK_PUBLICATION is YOUR publication, try the account")
            print("  that owns it, then run this again.")
        else:
            print(f"✓ Author session confirmed and saved to {PROFILE_DIR}")
            print("  substack_draft.py will reuse it from now on.")
        context.close()


if __name__ == "__main__":
    main()
