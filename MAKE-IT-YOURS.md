# Make it yours

Four things to set up. The first one takes two minutes and is the only one
that's required. The rest make it sound like you instead of like a tool.

---

## 1. Your publication and your one CTA  (2 minutes, required)

```bash
cp .env.example .env
```

Open `.env` and fill in:

- `SUBSTACK_PUBLICATION` — your subdomain, e.g. `janesmith.substack.com`. Look
  at your Substack URL; it's the bit before `.substack.com`.
- `MY_CTA_LABEL` and `MY_CTA_URL` — the ONE thing you want people to do at the
  end of a post. A membership, a waitlist, a service page, or just your
  subscribe link. **One.** Not three.
- `SPELLING` — `au` if you write in UK/Australian English, `us` if American,
  `off` if you don't want the gate policing spelling at all.

---

## 2. Your voice file  (optional — only topic mode needs it)

**Read this before you spend twenty minutes on it, because you probably don't
need to.**

Most of the time your voice is already in the source. Hand the skill your video,
your podcast, or your own social post, and that transcript is you talking. It
reads it twice — once for what you said, once for how you say things — and writes
in that voice. Nothing to set up.

The gap is **topic mode**: "write a substack about X" with no video, no episode,
no post. There's no transcript, so there's no voice signal in the material.

You have three ways to close that gap, and the free one is first:

**a) Talk it out for two minutes.** Open your voice memos, ramble about the topic
like you're explaining it to a friend, transcribe it, paste it in. You've just
made a transcript, which puts you back on the good path. Honestly this is the
best option — it's fast, and speaking gets more of your real voice out than
writing about your voice ever will.

**b) Point it at your published work.** "Read my last 5 Substack posts before you
write this one." No file needed.

**c) Build a voice file** — worth it only if you write from bare topics a lot and
you're sick of repeating yourself:

1. Find 10-20 pieces of writing that sound like you at your best. Real sent
   things — emails, captions, past newsletters — not things you drafted to sound
   impressive.
2. Put them in one folder.
3. Open Claude Code in this skill's folder and paste this:

> Read every file in `<folder>`. These are real things I've written. I want you
> to build me a voice file at `references/my-voice.md` that describes how I
> actually write, so an AI can write in my voice later.
>
> Cover: how I open (with 3 real examples), sentence rhythm, how long my
> paragraphs run, words and phrases I use a lot, how I handle emphasis, how I
> make a point land, how I close, and how formal I am.
>
> Then a BANNED list: words and constructions that appear nowhere in my writing
> but that AI reaches for constantly.
>
> Quote my real sentences as examples throughout. Don't describe my voice in
> the abstract — show it. And tell me the 3 things about my writing that would
> be hardest for an AI to fake.

4. Read it. Fix the bits it got wrong — you know your own voice better than it
   does.
5. Add a line at the top of `SKILL.md` under "Read first, every run":
   `3. references/my-voice.md — how I sound.`

If you make one, it's reusable in every other skill you build. That's the real
argument for it — not this skill, which mostly manages without.

---

## 3. Your banned words  (5 minutes)

Open `scripts/voice_gate_wordlist.json`. It already blocks the universal AI
tells. At the bottom there's an example rule under `"category": "mine"` — replace
it with a word you have personally decided you never write.

Everyone has one. A word that isn't wrong exactly, but isn't you. If you find
yourself editing it out of every draft, put it in the gate and stop thinking
about it.

```json
{ "pattern": "\\bquietly\\b", "severity": "ERROR", "category": "mine",
  "why": "flat and passive — it's never the right word for me" }
```

`severity` is `ERROR` (blocks and makes you fix it) or `WARN` (mentions it and
moves on). Patterns are regular expressions; `\\b` means "whole word only".

---

## 4. Path B — the browser bit  (10 minutes, optional)

Only if you want Claude to fill the Substack draft in for you rather than
handing you a copy page.

```bash
pip install playwright
python3 -m playwright install chromium
python3 scripts/substack_login.py
```

That last command opens a browser window at the Substack sign-in page. **You**
log in, the way you normally do. Press Enter in the terminal and the session is
saved to a browser profile inside this folder.

You never type your password into a script. The `.chrome-profile/` folder holds
that session and is git-ignored — it never leaves your machine, and it's the one
folder in here you should never share or commit.

To disconnect it later: `rm -rf .chrome-profile`. That's the whole revocation
process.

---

## What NOT to change

- **The gate is blocking on purpose.** If you find yourself wanting to skip it,
  the draft is the problem.
- **This skill never publishes.** Drafts only. Keep it that way until you've
  read enough of its output to trust it — and honestly, after that too. The
  10 seconds it costs you is the cheapest insurance there is.
