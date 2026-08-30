# Source: Podcast episode → Substack raw material

## Steps

1. **Identify the episode.** Take a Spotify/Apple episode URL, or "latest
   episode" → fetch the most recent. Get the title, description, and the audio
   URL.

   The Apple Podcasts lookup API is the easiest way to get an episode list plus
   a direct, DRM-free audio URL:
   ```bash
   curl -s "https://itunes.apple.com/lookup?id=<PODCAST_ID>&entity=podcastEpisode&limit=5" | \
     python3 -c "import json,sys; d=json.load(sys.stdin); [print(e.get('trackName'),'|',e.get('releaseDate','')[:10],'|',e.get('episodeUrl')) for e in d['results'][1:6]]"
   ```
   (Find `<PODCAST_ID>` in your show's Apple Podcasts URL — the number after `id`.)

2. **Get a transcript.** Download the audio, then transcribe locally:
   ```bash
   curl -sL -A "Mozilla/5.0" "<episode-audio-url>" -o /tmp/substack-pod.mp3
   whisper /tmp/substack-pod.mp3 --model small.en --language en \
     --output_dir /tmp/substack-pod-transcript --output_format txt
   ```
   Some podcast hosts redirect — `-L` and a real user-agent matter. If you get a
   4KB file back, you downloaded an HTML page, not audio.

   If your transcription is slow or unavailable, ask for a transcript rather
   than guessing at what was said. Never write about content you haven't read.

3. **Find the through-line — this is the whole job.** A podcast is a
   conversation; the Substack post is NOT a recap and NOT a transcript. Read the
   full transcript and pull the ONE strongest idea, hot take, or story. Build
   the article around THAT and let the rest go.

   If you find yourself writing "then we talked about…", start again.

4. **Links block** — 2-3 recent episodes, or recent videos if they're more
   relevant to the topic. Max 3.

5. **Images** — podcasts have no frames. The episode cover art works, or a
   pull-quote card, or nothing at all. Text-only is completely fine on Substack.
   Never invent a screenshot.

## Hand off

Give the writer: the transcript, the chosen through-line in one sentence, the
episode title and link, 2-3 links, and any image. It writes an essay around the
single strongest idea.

**Plus the voice markers**, pulled from the transcript — how they talk when
they're making this argument, their phrasings, and 3-5 real lines worth keeping.
A conversation is a rich voice sample; use it. See `references/substack-structure.md`
§ Voice comes from the source.

If it's an interview, be clear whose voice you're writing in — the host's, unless
they say otherwise. Don't blend two people into one narrator.
