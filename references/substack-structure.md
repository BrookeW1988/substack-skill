# The shared writer — structure, rules, and where YOUR voice goes

Every source (video / podcast / social / idea) hands its raw material to THIS
file. The sources gather; this file decides how the post reads.

## The one rule above all others

**Engaging, never flat.** Substack is article-first. People are choosing to
read, in a feed full of other people also choosing to be read. If a sentence
could appear in any generic AI blog post, rewrite it until it sounds like a
person actually talking.

The language gate (`scripts/voice_gate.py`) blocks the obvious slop. The gate is
the floor. The goal is a post worth reading even if they never click a link.

## Voice comes from the source — mine the transcript

This skill ships with NO personality baked in. It supplies structure. The sound
has to come from somewhere else, and for three of the four sources it's already
sitting in front of you.

**A video, a podcast, or a social post IS the person talking.** That transcript
is the best voice reference you will ever get — better than anything they could
write down about how they write. So read it TWICE:

1. **For content** — the argument, the examples, the numbers.
2. **For voice** — how they open, the words they reach for, their metaphors, the
   opinions they state flat, how they undercut themselves, what they emphasise,
   how long their thoughts run before they break.

Then write the article in THAT voice. Lift their real phrasings where they're
good. If they said something better out loud than you'd write it, use their line.

**What NOT to do:** don't transcribe speech into the article. Spoken language has
tangents, repetition, and filler that reads as sloppy on the page. You're taking
the voice MARKERS — word choice, rhythm, stance, humour — not the verbatim
sentences. The test: it should sound like them on a day they wrote carefully, not
like a transcript someone tidied.

Say in the report which source you took the voice from.

### The one mode with no voice signal

**Topic / idea / rant mode has no transcript.** There's nothing to mine. That's
the mode where a voice file earns its place — see `MAKE-IT-YOURS.md`. Options,
best first:

1. They have a voice file → load it.
2. No voice file, but they've published before → read 3-5 of their real pieces
   (past posts, emails, captions) and pull voice markers the same way.
3. Neither → ask them to talk the topic out for two minutes and paste the
   transcript. Now you're back to mining a transcript, which is the good path.
4. None of the above → write clean, plain, specific prose and SAY SO in the
   report. Never invent a persona.

## NO markdown in the body — except `## ` headings

Substack's editor renders most raw markdown as LITERAL TEXT. So write plain
prose, with one exception:

- **Section headings: DO use `## Heading text`.** The draft script types these
  with real keystrokes so the editor's input rule converts them into real styled
  H2s. Every post should have 3-5 of them breaking up the body. A wall of
  unbroken text is the fastest way to lose a reader.
- **Links:** a bare URL on its own line (videos become embeds this way), or
  `text — https://url` inline. NOT `[text](url)`.
- **Emphasis:** strong word choice, or CAPS if that's how you'd say it out loud.
  NOT `**bold**` / `*italic*`.
- **Bullets:** `- item` lines are fine.

## Why Substack is not email

The email conventions that do NOT translate:

- **"Hey friend," greetings** → open DIRECTLY with the hook or the idea.
- **The multi-offer P.S. stack** (course + masterclass + consult + …) → reads as
  bolted-on marketing. One CTA.
- **A heavy "in case you missed it" archive block** → keep it light and
  reader-useful, 3 links maximum, or skip it.
- **A sign-off** ("Catch you soon, [name]") → your byline is already on the
  page. A sign-off makes the article read like a newsletter someone pasted in.
  End on the last real line of the argument.

What DOES belong:

- A light "recently on my channel / on the pod" links block near the top, framed
  as helpful discovery, max 3 links.
- ONE clean call to action at the end. Just the one.

## The structure

```
# <Title — punchy, specific, front-loaded. See the playbook's title rules.>

<Direct hook opener — 1-4 short lines. An anecdote mid-action, a contrarian
claim, or a shocking specific number. NO greeting. This is make-or-break.>

<2-3 sentences framing the real unlock — not the surface topic.>

<A one-line lead-in, e.g. "Watch the full walkthrough below.">

<the bare video/episode URL ALONE on its own line — no "Watch:" prefix>
<a URL with text in front of it will NOT embed as a player>

*Recently, if you want to go deeper:*
- <link 1>
- <link 2>
- <link 3>

---

## <H2 — section 1: a real idea with a payoff>
<Short paragraphs. One-line paragraphs for punch. A real example or number
from the source material. Land the section on its strongest sentence.>

[IMAGE: name.jpg — descriptive alt]   ← only if it's clean and PII-free

## <H2 — section 2>
...

## <H2 — section 3>
...

---

## The quick version
- <recap bullet>
- <recap bullet>

<1-2 line close that lands the thesis.>

---

<ONE CTA. Yours, from MAKE-IT-YOURS.md. Give it a reason, not a naked button:
"Want the next teardown in your inbox?" beats "Subscribe".>

<SUBSCRIBE BUTTON — add a native Substack subscribe button at the end via the
editor's + menu. Don't write it as text; insert the real block.>

## NOTES TO SELF (delete before publishing)
- links used + verified
- image placement + PII confirmation
- gate result
```

## Before it goes anywhere

1. Run `scripts/voice_gate.py <draft.md>` — must exit 0. Fix every hit.
2. Confirm exactly ONE CTA, and the links block is 3 links or fewer.
3. Confirm no image shows PII.
4. Confirm there's a subtitle — one punchy sentence under the headline that adds
   NEW information instead of restating the title.
5. Build the preview so a human sees it before it reaches your account.
