import os, sys, json, time, html, requests
KEY = os.environ["AZURE_SPEECH_KEY"]
REGION = os.environ.get("AZURE_SPEECH_REGION", "eastus")
VOICE = os.environ.get("TTS_VOICE", "en-US-AnaNeural")
STYLE = os.environ.get("TTS_STYLE", "")
RATE = os.environ.get("TTS_RATE", "-8%")
PITCH = os.environ.get("TTS_PITCH", "+0%")
URL = f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

def ssml(text):
    inner = f'<prosody rate="{RATE}" pitch="{PITCH}">{html.escape(text)}</prosody>'
    if STYLE:
        inner = f'<mstts:express-as style="{STYLE}">{inner}</mstts:express-as>'
    return ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
            f'<voice name="{VOICE}">{inner}</voice></speak>')

def synth(text, path):
    for attempt in range(4):
        r = requests.post(URL, headers={
            "Ocp-Apim-Subscription-Key": KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "alp-tts"}, data=ssml(text).encode("utf-8"), timeout=60)
        if r.status_code == 200:
            open(path, "wb").write(r.content); return
        if r.status_code in (429, 503): time.sleep(3 * (attempt + 1)); continue
        raise SystemExit(f"HTTP {r.status_code}: {r.text[:300]}")
    raise SystemExit("gave up after retries")

prompts = json.load(open("scripts/tts/prompts.json", encoding="utf-8"))
if len(sys.argv) > 1 and sys.argv[1] == "--audition":
    os.makedirs("scripts/tts/audition", exist_ok=True)
    for i, (h, t) in enumerate(list(prompts.items())[:6]):
        p = f"scripts/tts/audition/{VOICE}{'-' + STYLE if STYLE else ''}-{i}.mp3"
        synth(t, p); print("wrote", p, "|", t)
    sys.exit(0)
out = "frontend/public/audio/prompts"
os.makedirs(out, exist_ok=True)
n = 0
for h, t in prompts.items():
    p = f"{out}/{h}.mp3"
    if os.path.exists(p) and os.path.getsize(p) > 500: continue
    synth(t, p); n += 1
    if n % 25 == 0: print(n, "done")
    time.sleep(0.15)
print("generated", n, "new files")
