# Developer by : Mr_Manas_Op
"""ffmpeg / ffprobe helpers: installation check and media inspection."""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
from dataclasses import dataclass

from services.errors import BotError

log = logging.getLogger(__name__)

_PROBE_TIMEOUT = 25
# Container formats that are playlists/manifests rather than plain media files.
_BLOCKED_FORMATS = {"hls", "applehttp", "dash", "concat", "ffconcat", "sdp", "rtsp", "rtp", "image2"}


@dataclass
class ProbeResult:
    duration: float
    has_audio: bool
    has_video: bool
    title: str
    artist: str


def check_installed() -> None:
    """Fail early with a clear message if ffmpeg/ffprobe are missing."""
    missing = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
    if missing:
        raise RuntimeError(
            f"Required program(s) not found: {', '.join(missing)}. "
            "Install ffmpeg (e.g. 'sudo apt install -y ffmpeg') and try again."
        )


async def probe(target: str, *, remote: bool) -> ProbeResult:
    """Inspect a media file or URL with ffprobe and validate that it is playable."""
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams"]
    if remote:
        cmd += ["-protocol_whitelist", "http,https,tcp,tls,crypto"]
    cmd += ["-i", target]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    except FileNotFoundError:
        log.error("ffprobe is not installed")
        raise BotError("Media tools are not installed on the server. Please contact the bot owner.") from None

    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=_PROBE_TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise BotError("Timed out while reading the media.") from None

    unreadable = BotError(
        "I couldn't read that media. Only direct links to audio or video files are supported."
    )
    if proc.returncode != 0:
        raise unreadable
    try:
        data = json.loads(stdout or b"{}")
    except json.JSONDecodeError:
        raise unreadable from None

    fmt = data.get("format") or {}
    if _BLOCKED_FORMATS & set(str(fmt.get("format_name", "")).split(",")):
        raise unreadable

    has_audio = has_video = False
    for stream in data.get("streams", []):
        kind = stream.get("codec_type")
        if kind == "audio":
            has_audio = True
        elif kind == "video" and not (stream.get("disposition") or {}).get("attached_pic"):
            has_video = True
    if not (has_audio or has_video):
        raise unreadable

    try:
        duration = float(fmt.get("duration") or 0)
    except (TypeError, ValueError):
        duration = 0.0
    tags = {str(k).lower(): str(v) for k, v in (fmt.get("tags") or {}).items()}
    return ProbeResult(duration, has_audio, has_video, tags.get("title", ""), tags.get("artist", ""))
