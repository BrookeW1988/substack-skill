#!/usr/bin/env python3
"""
substack_draft.py — PATH B: fill a Substack DRAFT for you (Playwright).

Opens Chrome with the session you saved via substack_login.py, goes to your
publication's post editor, types the title and the body, and lets Substack
autosave it as a draft. Then it stops and prints the draft URL.

IT DOES NOT PUBLISH. You review the draft and press the button yourself.

Run:
  python3 substack_draft.py --md <draft.md> --title "<title>"
  python3 substack_draft.py --md <draft.md> --title "..." --pub other.substack.com

Setup: copy .env.example to .env, set SUBSTACK_PUBLICATION, then run
substack_login.py once. Needs playwright installed.

Images are NOT auto-uploaded — the body gets visible "[ ADD IMAGE: name ]" lines
and you drag each one in. The preview page shows exactly where they go.

If anything fails it screenshots /tmp/substack-draft-error.png and exits 1, so
you fall back to Path A (the copy page). The post is already written either way.
"""

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = SKILL_DIR / ".env"
PROFILE_DIR = SKILL_DIR / ".chrome-profile"

YT = re.compile(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+")


def read_env(key: str, default: str | None = None):
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key:
                return v.strip()
    return default


def parse_body(md: str):
    """Turn the draft markdown into (kind, text) blocks the editor can take."""
    out, buf = [], []

    def strip_md(s: str) -> str:
        # Substack shows raw markdown as literal text, so flatten it.
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", s)
        s = re.sub(r"^[-*]\s+", "• ", s)
        return s

    def flush():
        if buf:
            out.append(("p", strip_md(" ".join(buf).strip())))
            buf.clear()

    for raw in md.splitlines():
        line = raw.rstrip()

        if re.match(r"^#{1,3}\s*NOTES (TO SELF|FOR ME)", line, re.I):
            break

        img = re.match(r"^\[IMAGE:\s*([^\]\s]+)", line)
        if img:
            flush()
            out.append(("img", img.group(1)))
            continue

        h = re.match(r"^(#{1,3})\s+(.*)$", line)
        if h:
            flush()
            out.append(("h", h.group(2)))
            continue

        if line.strip() == "---":
            flush()
            out.append(("hr", ""))
            continue

        if line.strip() == "":
            flush()
            continue

        # bullets are their own block so they don't merge into one paragraph
        if re.match(r"^\s*[-*]\s+", line):
            flush()
            out.append(("p", strip_md(line.strip())))
            continue

        buf.append(line)

    flush()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--pub", help="publication subdomain (default: SUBSTACK_PUBLICATION from .env)")
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()

    pub = a.pub or read_env("SUBSTACK_PUBLICATION")
    if not pub or "yourname" in pub:
        sys.exit(
            "No publication set. Copy .env.example to .env and set\n"
            "  SUBSTACK_PUBLICATION=yourname.substack.com\n"
            "(or pass --pub). Path A needs none of this."
        )
    if not PROFILE_DIR.exists():
        sys.exit(
            "No saved session. Run the one-time login first:\n"
            f"  python3 {SKILL_DIR}/scripts/substack_login.py"
        )

    md_path = Path(a.md)
    if not md_path.exists():
        sys.exit(f"draft not found: {md_path}")
    blocks = parse_body(md_path.read_text())

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "Playwright isn't installed — use Path A (the copy page) instead, "
            "or: pip install playwright && python3 -m playwright install chromium"
        )

    with sync_playwright() as pw:
        # Persistent profile keeps the author session (including the httpOnly
        # cookie) on disk between runs. You log in once via substack_login.py.
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR), headless=a.headless, slow_mo=25
        )
        page = context.pages[0] if context.pages else context.new_page()

        editor_url = f"https://{pub}/publish/post"
        print(f"Opening the editor at {editor_url} …")
        page.goto(editor_url, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # A non-author hits a "this page is private" sign-in wall.
        if page.get_by_text(
            re.compile(r"this page is private|sign in to", re.I)
        ).first.is_visible(timeout=2500):
            print(
                "ERROR: not logged in as the author of this publication.\n"
                f"Run: python3 {SKILL_DIR}/scripts/substack_login.py\n"
                "Falling back to the copy page for now — the post is still ready.",
                file=sys.stderr,
            )
            context.close()
            sys.exit(1)

        try:
            title_field = page.locator('[data-testid="post-title"]').first
            title_field.click(timeout=10000)
            title_field.fill(a.title)
            page.wait_for_timeout(600)

            editor = page.locator('[data-testid="editor"]').first
            editor.click()
            page.wait_for_timeout(400)

            # Put the caret at the very start of the empty editor.
            page.evaluate(
                """() => {
                    const ed = document.querySelector('[data-testid="editor"]')
                            || document.querySelector('[contenteditable="true"]');
                    ed.focus();
                    const sel = window.getSelection();
                    const r = document.createRange();
                    r.selectNodeContents(ed); r.collapse(true);
                    sel.removeAllRanges(); sel.addRange(r);
                }"""
            )

            def insert_text(s):
                # Fast bulk insert at the caret. NEVER use .fill() on the body —
                # it replaces the whole editor and wipes what's already there.
                page.evaluate("(s)=>document.execCommand('insertText', false, s)", s)

            embed_urls = []
            for kind, text in blocks:
                if kind == "img":
                    insert_text(f"[ ADD IMAGE: {text} ]")
                    page.keyboard.press("Enter")
                elif kind == "hr":
                    insert_text("—")
                    page.keyboard.press("Enter")
                elif kind == "h":
                    # Real keystrokes so the "## " input rule fires and makes a real H2.
                    page.keyboard.type("## ", delay=15)
                    page.wait_for_timeout(120)
                    insert_text(text)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(150)
                else:
                    if YT.fullmatch(text.strip()):
                        embed_urls.append(text.strip())
                    insert_text(text)
                    page.keyboard.press("Enter")
                page.wait_for_timeout(60)

            page.wait_for_timeout(1200)

            # Video URLs are left as clean bare-URL lines on purpose. Substack's
            # embed fires on its own paste handler, which synthetic input doesn't
            # reliably trigger (it sometimes embeds, sometimes stays text, and
            # sometimes DOUBLES the URL). Clicking the line + Enter always works.

            # Subscribe button, at the very end. Move the caret to the true end of
            # the document first — otherwise the button lands mid-post.
            try:
                page.evaluate(
                    """() => {
                        const ed = document.querySelector('[data-testid="editor"]');
                        ed.focus();
                        const sel = window.getSelection();
                        const r = document.createRange();
                        r.selectNodeContents(ed); r.collapse(false);  // false = end
                        sel.removeAllRanges(); sel.addRange(r);
                    }"""
                )
                page.wait_for_timeout(300)
                page.keyboard.press("Enter")
                page.wait_for_timeout(300)
                btn = page.get_by_role("button", name=re.compile(r"^Button$")).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    page.wait_for_timeout(900)
                    sub = page.get_by_text(re.compile(r"^Subscribe", re.I)).first
                    if sub.is_visible(timeout=2500):
                        sub.click()
                        page.wait_for_timeout(1300)
                        print("✓ Subscribe button added at the end")
            except Exception as be:
                print(f"  (couldn't auto-add the subscribe button: {be})", file=sys.stderr)

            page.wait_for_timeout(2500)  # let Substack autosave
            draft_url = page.url
            print(f"\n✓ DRAFT created and autosaved: {draft_url}")
            print("RESULT_DRAFT_URL=" + draft_url)

            print("\n── Left for you (about a minute) ──")
            if embed_urls:
                print("Turn these into video players: click the END of each line in the")
                print("editor and press Enter.")
                for u in embed_urls:
                    print(f"   • {u}")
            print("Drag your images onto the [ ADD IMAGE: ... ] lines.")
            print("Add the subtitle under the headline.")
            print("Set a cover image, then Preview → Publish. Nothing publishes without you.")
            page.wait_for_timeout(3000)

        except Exception as e:
            shot = "/tmp/substack-draft-error.png"
            try:
                page.screenshot(path=shot, full_page=True)
            except Exception:
                pass
            print(
                "ERROR: couldn't drive the Substack editor (the selectors may have changed).\n"
                f"Screenshot: {shot}\n"
                "Fall back to the copy page — the post itself is fine.\n"
                f"{e}",
                file=sys.stderr,
            )
            context.close()
            sys.exit(1)

        context.close()


if __name__ == "__main__":
    main()
