# substack — one piece of content → a post worth reading

A Claude Code skill that turns a YouTube video, a podcast episode, your
best-performing social post, or just a topic you want to rant about into a
Substack post shaped the way Substack posts actually work.

It writes the post, checks it for AI-slop language, and then hands it to you one
of two ways. **It never publishes. You press the button.**

## The two ways

**Path A — the copy page.** You get a local web page with the finished post on
it and a big "Copy whole post" button. Click, open Substack, paste. Nothing
installed, nothing logged in, nothing touching your account. This is the default
and it's a perfectly good way to run this forever.

**Path B — the browser.** Claude opens a real Chrome window, goes to your
Substack editor and types the post in for you as a draft. You log in once, by
hand. It still stops at draft.

Start with A. Move to B if and when the copying starts to annoy you.

## The easy way to set it up

1. Download this repo (green **Code** button → **Download ZIP**) and unzip it
   into `~/.claude/skills/substack/`
2. Open Claude Code and say:
   *"read the substack skill and set it up for me — I want to start with the
   copy-page path"*
3. Then: *"write a substack post from this video: &lt;URL&gt;"*

Claude reads `MAKE-IT-YOURS.md` and walks you through the rest.

## The even-more-yours way

Open `prompts/build-your-own.md` and paste that prompt into Claude Code. It
builds the same workflow wired to your own sources and tools rather than
installing this one verbatim.

## What's inside

- `SKILL.md` — the orchestrator: both paths, the rules, the failure modes
- `MAKE-IT-YOURS.md` — your publication, your CTA, your voice, your banned words
- `references/substack-structure.md` — how the post is shaped and why Substack
  isn't email
- `references/substack-performance-playbook.md` — the format menu, title rules,
  length targets and Notes strategy, with sources
- `sources/` — one file per input type (video, podcast, social post, topic)
- `scripts/build_preview.py` — the copy page
- `scripts/voice_gate.py` + `voice_gate_wordlist.json` — the blocking language gate
- `scripts/substack_draft.py` + `substack_login.py` — Path B
- `prompts/build-your-own.md` — the rebuild-it-yourself prompt

## You'll need

- [Claude Code](https://claude.com/claude-code)
- Python 3 (already on a Mac)
- Path A needs nothing else.
- Path B also needs `pip install playwright` and a one-time login.
- Transcribing video or audio yourself needs `yt-dlp` and Whisper
  (`brew install yt-dlp`, `pip install openai-whisper`).

No API keys. No accounts beyond your own Substack. Nothing leaves your machine
until you publish.

## A note on voice

This skill ships with no personality in it on purpose — but it doesn't need one,
because most of the time your voice is already in the source.

If you hand it your video, your podcast, or your own post, that transcript is you
talking. The skill reads it twice — once for what you said, once for HOW you say
things — and writes the article in that voice. No setup, nothing to prepare.

The exception is writing from a bare topic, where there's no transcript to work
from. For that there's an optional voice file (`MAKE-IT-YOURS.md`), or you can
just talk the topic out for two minutes and paste the transcript in — which puts
you back on the good path. If there's nothing to go on at all, you get clean plain
prose and the skill tells you that's what happened.
