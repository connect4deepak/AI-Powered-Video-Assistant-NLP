import os
import subprocess
import yt_dlp
from pydub import AudioSegment

# ── Resolve ffmpeg path once ──────────────────────────────────────────────────
_ffmpeg_path = subprocess.run(
    ["which", "ffmpeg"], capture_output=True, text=True
).stdout.strip()

# Fallback to Homebrew default if `which` comes up empty
FFMPEG_PATH = _ffmpeg_path or "/opt/homebrew/bin/ffmpeg"

# Tell pydub where ffmpeg lives
AudioSegment.converter = FFMPEG_PATH

DOWNLOAD_DIR = "downloads"          # fixed typo: "downloades" → "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ── YouTube download ──────────────────────────────────────────────────────────
def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "cookiefile": "cookies.txt",
        "remote_components": ["ejs:github"],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "ffmpeg_location": FFMPEG_PATH,   # ✅ FIX: tell yt-dlp where ffmpeg is  # <-- Add this
        "quiet": False,                       # Helpful for debugging

    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # yt-dlp renames the file after postprocessing; reflect that here
        for ext in (".webm", ".m4a", ".mp4", ".opus"):
            filename = filename.replace(ext, ".wav")
    return filename


# ── Local file → WAV ──────────────────────────────────────────────────────────
def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16 kHz mono
    audio.export(output_path, format="wav")
    return output_path


# ── Chunker ───────────────────────────────────────────────────────────────────
def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


# ── Entry point ───────────────────────────────────────────────────────────────
def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks