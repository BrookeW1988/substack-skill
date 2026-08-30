#!/usr/bin/env python3
"""
build_preview.py — turn a draft .md into a self-contained HTML page with
one-click copy buttons and inline images.

This is the heart of PATH A (no automation): you click "Copy whole post", open
Substack, and paste. It's also the human review surface before Path B touches
your account.

Usage:
  python3 build_preview.py --md <draft.md> [--images <dir>] --out <index.html> [--serve]

The .md uses [IMAGE: filename.jpg — alt text] markers; each is matched to a file
in --images and embedded inline (base64) at that spot. A trailing
"NOTES TO SELF" block is dropped from the output.

No dependencies beyond the Python standard library.
"""

import argparse
import base64
import html
import re
import sys
from pathlib import Path

YT = re.compile(r"^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+$")


def md_inline(text: str) -> str:
    """Minimal inline markdown → HTML: links, bold, italic."""
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def b64_img(path: Path) -> str:
    data = path.read_bytes()
    ext = path.suffix.lstrip(".").lower() or "jpeg"
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(data).decode()


def render(md: str, images_dir: Path | None):
    """Returns (title, body_html, missing_images, embed_urls)."""
    m = re.search(r"^#{1,3}\s*NOTES (TO SELF|FOR ME)", md, re.M | re.I)
    if m:
        md = md[: m.start()]

    title = ""
    out, para, missing, embeds = [], [], [], []

    def flush():
        if para:
            out.append("<p>" + md_inline(" ".join(para).strip()) + "</p>")
            para.clear()

    for raw in md.split("\n"):
        line = raw.rstrip()

        h1 = re.match(r"^#\s+(.*)$", line)
        if h1 and not title:
            title = h1.group(1).strip()
            continue

        h = re.match(r"^(#{2,3})\s+(.*)$", line)
        if h:
            flush()
            lvl = len(h.group(1))
            out.append(f"<h{lvl}>{md_inline(h.group(2))}</h{lvl}>")
            continue

        img = re.match(r"^\[IMAGE:\s*([^\]\s]+)", line)
        if img:
            flush()
            name = img.group(1)
            alt_m = re.search(r"—\s*(.+?)\]", line)
            alt = html.escape(alt_m.group(1)) if alt_m else ""
            if images_dir and (images_dir / name).exists():
                out.append(
                    f'<img src="{b64_img(images_dir / name)}" alt="{alt}" '
                    'style="max-width:100%;border-radius:8px;'
                    'box-shadow:0 2px 10px rgba(0,0,0,.08);margin:18px 0;">'
                )
            else:
                missing.append(name)
                out.append(
                    '<p class="imgnote">[ image: '
                    + html.escape(name)
                    + " — drag this one in yourself ]</p>"
                )
            continue

        if line.strip() == "---":
            flush()
            out.append("<hr>")
            continue

        if line.strip().startswith("- "):
            flush()
            out.append("<ul><li>" + md_inline(line.strip()[2:]) + "</li></ul>")
            continue

        if line.strip() == "":
            flush()
            continue

        if YT.match(line.strip()):
            flush()
            embeds.append(line.strip())
            out.append(f'<p class="embedline">{html.escape(line.strip())}</p>')
            continue

        para.append(line)

    flush()
    return title, "\n".join(out), missing, embeds


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light; }}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  max-width:740px;margin:0 auto;padding:0 24px 80px;color:#1a1a1a;line-height:1.65;}}
.bar{{position:sticky;top:0;background:#fff;padding:14px 0;border-bottom:1px solid #e8e8e8;
  display:flex;gap:10px;align-items:center;flex-wrap:wrap;z-index:10;}}
button{{background:#FF6719;color:#fff;border:0;padding:10px 16px;border-radius:6px;
  font-size:14px;font-weight:600;cursor:pointer;}}
button.ghost{{background:#fff;color:#333;border:1px solid #d5d5d5;}}
button:hover{{filter:brightness(.93);}}
.status{{font-size:13px;color:#666;flex:1 1 100%;}}
.steps{{background:#fbf7f2;border:1px solid #f0e4d6;border-radius:10px;padding:16px 20px;margin:22px 0;font-size:14px;}}
.steps h3{{margin:0 0 8px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#a0562a;}}
.steps ol{{margin:0;padding-left:20px;}} .steps li{{margin:5px 0;}}
h1.t{{font-size:31px;line-height:1.25;margin:26px 0 8px;}}
h2{{font-size:22px;margin-top:1.7em;}} h3{{font-size:18px;}}
hr{{border:0;border-top:1px solid #ececec;margin:30px 0;}}
ul{{margin:6px 0;}}
.imgnote{{background:#fff8e1;border-left:3px solid #f0b429;padding:9px 12px;
  border-radius:4px;font-size:14px;color:#7a5b13;}}
.embedline{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px;
  background:#f4f6f8;border-left:3px solid #7aa7c7;padding:9px 12px;border-radius:4px;
  word-break:break-all;}}
</style></head><body>

<div class="bar">
  <button onclick="copyPost()">Copy whole post</button>
  <button class="ghost" onclick="copyTitle()">Copy title</button>
  <span class="status" id="status">Copy &rarr; open Substack &rarr; paste into a new post.</span>
</div>

<div class="steps">
  <h3>After you paste</h3>
  <ol>
    {todo}
    <li>Add a <strong>subtitle</strong> under the headline — one line that adds
        something new, not a restatement of the title.</li>
    <li>Add a native <strong>Subscribe button</strong> at the end
        (the <strong>+</strong> menu in the editor &rarr; Button).</li>
    <li>Set a cover image, then Preview &rarr; Publish.</li>
  </ol>
</div>

<h1 class="t">{title}</h1>
<div id="post">{body}</div>

<script>
function flash(msg){{ document.getElementById('status').textContent = msg; }}
function copyPost(){{
  const el=document.getElementById('post');
  const r=document.createRange(); r.selectNode(el);
  const s=window.getSelection(); s.removeAllRanges(); s.addRange(r);
  try{{ document.execCommand('copy'); flash('Copied. Paste it into the Substack editor.'); }}
  catch(e){{ flash('Copy failed — select it manually and copy.'); }}
  s.removeAllRanges();
}}
function copyTitle(){{
  navigator.clipboard.writeText({title_json})
    .then(()=>flash('Title copied.'))
    .catch(()=>flash('Copy failed — select it manually.'));
}}
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--images")
    ap.add_argument("--out", required=True)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8771)
    a = ap.parse_args()

    md_path = Path(a.md)
    if not md_path.exists():
        sys.exit(f"draft not found: {md_path}")

    images_dir = Path(a.images) if a.images else None
    title, body, missing, embeds = render(md_path.read_text(), images_dir)

    todo = []
    if embeds:
        todo.append(
            "<li>Turn each video URL into a player: click the END of that line "
            "in the editor and press <strong>Enter</strong>. "
            f"({len(embeds)} to do.)</li>"
        )
    if missing:
        todo.append(
            "<li>Drag your images onto the highlighted [ image: ... ] lines: "
            + html.escape(", ".join(missing))
            + "</li>"
        )

    import json as _json

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        PAGE.format(
            title=html.escape(title or "Substack post"),
            title_json=_json.dumps(title or ""),
            body=body,
            todo="\n    ".join(todo),
        )
    )
    print(f"wrote {out}")
    if embeds:
        print(f"video URLs to Enter on after pasting: {len(embeds)}")
    if missing:
        print(f"images to drag in: {', '.join(missing)}")

    if a.serve:
        import http.server
        import os
        import socketserver

        os.chdir(out.parent)
        with socketserver.TCPServer(("", a.port), http.server.SimpleHTTPRequestHandler) as httpd:
            url = f"http://localhost:{a.port}/{out.name}"
            print(f"serving at {url}  (ctrl-c to stop)")
            if sys.platform == "darwin":
                os.system(f"open '{url}'")
            httpd.serve_forever()


if __name__ == "__main__":
    main()
