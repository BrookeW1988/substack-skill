---
name: substack
description: >-
  Turn one piece of content — a YouTube video, a podcast episode, your
  best-performing social post, or just a topic you want to rant about — into an
  engaging Substack post in YOUR voice. Two paths: write the draft and hand you
  a one-click copy page to paste in yourself, or drive your logged-in browser
  and build the draft in Substack for you. Use when you say "write a Substack
  post", "turn this video into a Substack", "substack from my podcast", or
  "write a substack about X".
user-invocable: true
argument-hint: <youtube-url | podcast <url> | social | about <topic>
---

# /substack — one piece of content → a Substack post worth reading

This skill does the thinking part (what the post should SAY and how it should
read) and then gets it into Substack one of two ways. It never publishes for
you — you always press the button.

## The two paths

Pick one at the start of every run. If the person hasn't said, **ask once** and
default to Path A.

### Path A — Draft + copy page (no automation, no setup)
The skill writes the post, checks it against the language gate, and builds a
local HTML page with a **"Copy whole post"** button. Click it, open Substack,
paste. Done. Nothing installed, nothing logged in, nothing touching your
account.

**This is the default and it's a completely legitimate way to run this skill
forever.** The copy page is not a consolation prize — it's the review surface
you'd want anyway.

### Path B — Browser path (Claude fills the draft in for you)
Claude opens a real Chrome window, goes to your Substack editor, and types the
title and body in for you as a DRAFT. You log in ONCE by hand; after that it
reuses that session. It stops at draft — you review and press Publish.

Path B needs `pip install playwright` + a one-time login (see
`MAKE-IT-YOURS.md`). If anything about it fails, the skill falls back to Path A
automatically. Nothing is lost — the post is already written.

## Read first, every run

1. `references/substack-structure.md` — how the post is shaped, and the rules
   about what does NOT translate from email to Substack.
2. `references/substack-performance-playbook.md` — the format menu, title
   rules, length targets, Notes strategy. Researched, with sources.
3. `MAKE-IT-YOURS.md` (once, at setup) — your publication, your CTA, your
   banned words, your voice file.

## The flow

```
/substack <source>
  │
  1. DETECT the source type
  │    youtube url → video · podcast url → podcast · "social" → best post
  │    no url, just a topic → idea (general article mode)
  │
  2. GATHER raw material  (sources/<type>.md)
  │
  3. WRITE it  (references/substack-structure.md + your own voice file)
  │
  4. GATE it  (scripts/voice_gate.py — blocks on AI-slop language)
  │
  5. PREVIEW it  (scripts/build_preview.py → local page with a Copy button)
  │
  6a. PATH A: you paste it in.  ← default
  6b. PATH B: scripts/substack_draft.py fills the draft for you.
  │
  7. COMPANION NOTES — draft 2 Substack Notes to post after you publish
  │
  8. REPORT — what it used, gate result, the notes, what's left for you to do
```

## Step 1 — detect the source

| The input | Mode | Read |
|---|---|---|
| contains `youtube.com` / `youtu.be` | video | `sources/from-video.md` |
| contains `spotify.com` / `podcasts.apple.com` / `pod.link`, or says "podcast" | podcast | `sources/from-podcast.md` |
| says `social` / `best post` / `top post` | social | `sources/from-social-post.md` |
| no URL, just a topic or a rant | idea | `sources/from-idea.md` **and** the playbook |
| ambiguous | — | ask which of the four |

## Step 2-3 — gather, then write

Each file in `sources/` has ONE job: produce the raw material (a transcript, a
post's text, the beats, any images). It does NOT decide how the post reads.

`references/substack-structure.md` is the shared writer — same structure and
same rules no matter where the material came from. Don't reinvent the writing
rules per source.

**Voice is yours, not this skill's.** The structure file tells you the shape;
your own voice file (see `MAKE-IT-YOURS.md`) tells you the sound. If you
haven't made one yet, the skill writes in clean plain prose and says so in the
report — it does NOT invent a personality for you.

## Step 4 — the language gate (BLOCKING)

```bash
python3 scripts/voice_gate.py <draft.md>
```

Exits non-zero and lists every hit if it finds AI-slop language ("dive in",
"game-changing", "unlock", "in today's fast-paced world", "Whether you're X, Y
or Z", "it's important to note"…), US spelling if you've set that preference,
or anything you've added to your own banned list.

**Fix every hit before the post goes anywhere.** Do not bypass the gate. The
words live in `scripts/voice_gate_wordlist.json` — add your own there (there's
an example inside).

Why this matters: readers pattern-match AI writing fast, and trust drops
sharply the moment they suspect it. The gate is the floor, not the goal.

## Step 5 — build the preview (BOTH paths)

```bash
python3 scripts/build_preview.py \
  --md <draft.md> --images <image-dir> --out /tmp/substack-<slug>/index.html --serve
```

A self-contained HTML page: the post rendered as it'll read, images embedded
inline, and a **Copy whole post** button at the top. It opens in your browser.

- On Path A this IS the delivery — copy, paste into Substack, add images.
- On Path B it's the review gate before Claude touches your account.

## Step 6b — Path B only: fill the draft in Substack

```bash
python3 scripts/substack_draft.py --md <draft.md> --title "<title>"
# publication comes from .env (SUBSTACK_PUBLICATION), override with --pub
```

What it does: opens Chrome with your saved session, goes to your publication's
`/publish/post` editor, types the title, then types the body block by block so
`## ` headings become real styled H2s. Substack autosaves it as a draft. It
prints the draft URL and stops.

Things that are true about the Substack editor (learned the hard way — don't
re-litigate them):

- The editor lives on **your publication's subdomain** (`yourpub.substack.com/publish/post`).
  The generic `substack.com/publish/post` redirects away and fails.
- Selectors: title = `[data-testid="post-title"]`, body = `[data-testid="editor"]`.
- Insert body text with `execCommand('insertText')` at the caret. Do NOT use
  Playwright's `.fill()` on the body — it REPLACES the whole editor and wipes
  what's already there.
- Headings need REAL keystrokes (`## ` typed with a delay) so the editor's
  markdown input rule fires. Pasted `## ` stays literal text.
- Automated email+password login tends to land you as a READER, not the author.
  That's why setup is a one-time manual login into a persistent browser profile.
- Video URLs: leave each on its OWN line, bare, with no text in front. To turn
  one into an embedded player, click the end of that line in the editor and
  press Enter. Synthetic paste does not reliably trigger the embed — so the
  script leaves clean URL lines and tells you which ones to Enter on.
- Images are not auto-uploaded. The body gets `[ ADD IMAGE: name ]` lines and
  you drag each one in. The preview page shows exactly where they go.

If anything fails, the script screenshots `/tmp/substack-draft-error.png`,
exits 1, and you fall back to Path A. The post is still 100% ready.

## Step 7 — companion Notes (both paths)

Every article ships with **2 draft Notes**. Notes are Substack's growth engine —
roughly half of new free subscriptions come through the in-app network, and
creators routinely trace more subscribers to Notes than to posts. Formats and
sources are in the playbook.

1. **Note A — standalone value.** The article's sharpest idea as a story, a
   contrarian take, or a quick fix. Must be worth reading even if they never
   click. No link, or a link right at the end.
2. **Note B — "new post" teaser.** 2-4 punchy lines + the post URL.

Both notes go through the same gate. Plain text, first line is the hook, short
lines, no hashtags, no markdown.

**Notes have no draft state on Substack** — posting one is instant and public.
So this skill NEVER posts them. It hands you the text; you paste it into the
Notes composer when you're ready.

Also worth doing: restack your own post the morning after it goes out.

## Step 8 — report

- The draft URL (Path B) or the preview URL (Path A)
- What it pulled from and what it found
- The format it chose and why (general article mode)
- Gate result — article AND both notes
- The 2 notes, ready to paste
- Anything still on you: images to drag in, video lines to Enter on, the
  subscribe button, the subtitle

## Non-negotiables

1. **Engaging or nothing.** If a sentence could appear in any generic AI blog
   post, rewrite it. Substack is article-first — the post has to be worth the
   read even if they never click a single link.
2. **Article-first structure.** Open directly with the hook. No "Hey friend".
   No multi-offer P.S. stack. Those are email conventions and they read as
   bolted-on marketing here.
3. **ONE call to action**, at the end. One. Set it in `MAKE-IT-YOURS.md`.
4. **No sign-off.** No "Catch you soon, [name]". Your byline is already on the
   page — a sign-off makes an article read like a newsletter someone pasted in.
5. **No PII in images.** Check every frame for real emails, names, account
   numbers, client data. Drop anything that shows them.
6. **Never fabricate.** No invented stats, client results, or revenue figures.
   If a load-bearing claim can't be verified, cut it or reframe it as opinion.
7. **The gate is blocking.** Fix hits, don't bypass.
8. **Draft only.** This skill does not publish. You press the button.

## Files

```
SKILL.md                                ← this orchestrator
MAKE-IT-YOURS.md                        ← your publication, CTA, voice, banned words
README.md                               ← start here if you're new
.env.example                            ← copy to .env (Path B only)
references/
  substack-structure.md                 ← the shared writer: shape + rules
  substack-performance-playbook.md      ← what performs, with sources
sources/
  from-video.md                         ← YouTube → raw material
  from-podcast.md                       ← podcast → raw material
  from-social-post.md                   ← your best post → expanded essay
  from-idea.md                          ← a topic or a rant → original article
scripts/
  build_preview.py                      ← draft.md → HTML page with a Copy button
  voice_gate.py                         ← BLOCKING language gate
  voice_gate_wordlist.json              ← the banned list (add your own here)
  substack_draft.py                     ← Path B: fill the draft in Substack
  substack_login.py                     ← Path B: one-time login
prompts/
  build-your-own.md                     ← rebuild this around your own stack
```

## Failure modes

| What happened | Do this |
|---|---|
| Playwright not installed / not logged in | Fall back to Path A. Don't block the run on it. |
| Editor selectors changed | Screenshot, exit 1, fall back to Path A, tell them what broke. |
| No transcript available | Whisper the audio locally, or ask for a transcript. Never guess at content. |
| PII in a frame | Drop that frame. Pick another. Never feature it. |
| Gate fails | Rewrite the offending lines. Never bypass. |
| Topic too vague | Ask ONE angle question (what happened / what's the take / who's it for). Don't write a generic explainer nobody asked for. |
| A claim can't be verified | Cut it, or reframe as opinion. |
