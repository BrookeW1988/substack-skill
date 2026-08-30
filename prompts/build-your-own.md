# Build this around YOUR workflow

Instead of installing this skill as-is, you can paste the prompt below into
Claude Code and have it build a version wired to your own tools, your own
sources, and your own publishing habits.

---

I want a "substack" skill for Claude Code that turns one piece of content into
a Substack post I'd actually be happy to publish. Build it using this outcome
spec:

1. INPUT — any of: a YouTube URL, a podcast episode URL, my best-performing
   social post, or just a topic I want to rant about. Detect which one I've
   given you.

2. RAW MATERIAL — for video and podcast, get a transcript (captions if they
   exist, otherwise local Whisper). For a social post, take the text and its
   numbers. For a topic, interview me for the angle in ONE question, then pull
   real receipts from my own files rather than inventing any.

3. WRITE — article-first, not email-shaped. Direct hook opener with no
   greeting, 3-5 section headings, short paragraphs, one call to action at the
   end, no sign-off. Ask me for examples of my own writing and build a voice
   file from them before you write a word.

4. GATE — before anything ships, check the draft against a list of AI-slop
   words and block on hits. Make the list a file I can edit, and ask me which
   words I've personally banned so you can seed it.

5. HAND IT OVER — two ways, my pick:
   (a) build a local HTML page of the finished post with a one-click "copy
       whole post" button and images embedded inline, so I paste it in myself;
   (b) drive my logged-in browser and fill the Substack draft for me — title,
       body, headings — then stop. Never publish. I press the button.

6. NOTES — write me 2 Substack Notes to go with each post: one that stands on
   its own value, one that teases the post with the link. Don't post them;
   Notes have no draft state and go live instantly.

Ask me: my Substack URL, what my ONE call to action is, whether I write in UK
or US spelling, and where I want drafts saved.
