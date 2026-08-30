# Source: YouTube video → Substack raw material

Gather the material from a published video, then hand it to
`references/substack-structure.md` to write.

## Steps

1. **Get the transcript.** If another skill already transcribed this video this
   session, reuse it. Otherwise pull the captions:
   ```bash
   yt-dlp --write-auto-sub --sub-lang en --skip-download \
     --sub-format vtt -o "/tmp/substack-%(id)s.%(ext)s" "<url>"
   ```
   No captions? Download the audio and transcribe it locally:
   ```bash
   yt-dlp -x --audio-format mp3 -o "/tmp/substack-audio.mp3" "<url>"
   whisper /tmp/substack-audio.mp3 --model small.en --language en \
     --output_dir /tmp/substack-transcript --output_format txt
   ```

2. **Get the metadata** (title, description, chapters):
   ```bash
   yt-dlp --no-warnings -J --skip-download "<url>" | python3 -c \
     "import json,sys; d=json.load(sys.stdin); print(d['title']); print(d.get('description',''))"
   ```

3. **Get 2-3 links for the "recently" block** — your most recent OTHER uploads:
   ```bash
   yt-dlp --flat-playlist -J "https://www.youtube.com/@<your-handle>/videos" | python3 -c \
     "import json,sys; d=json.load(sys.stdin); [print(e['title'],'—','https://youtu.be/'+e['id']) for e in d['entries'][:5]]"
   ```

4. **Frames (optional images).** Pull a handful of stills and pick 2-3 that
   illustrate the key sections:
   ```bash
   ffmpeg -i <video.mp4> -vf "fps=1/60,scale=1280:-1" /tmp/substack-frames/frame-%03d.jpg
   ```
   **Look at every candidate frame and check for PII** — real emails, names,
   account numbers, client data, anything on a visible screen. Drop any frame
   that shows them. This is not optional and it is not a spot check.

5. **Companion written version.** If you published a blog post or written
   version of this video, grab the real URL and link it as "read the written
   version". Never link a URL you haven't confirmed exists.

## Hand off

Give the writer: the transcript, the title, 2-3 recent links, the video URL, the
written-version URL if there is one, and the PII-checked images with alt text.

A tutorial video usually wants a 3-section shape — the three things it actually
teaches, each with its own H2 and a real example from the transcript.
