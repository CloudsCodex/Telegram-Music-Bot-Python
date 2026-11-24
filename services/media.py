# Developer by : Mr_Manas_Op
"""Media probing, Telegram file downloads and temporary-file cleanup."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path

from config import get_config
from services import ffmpeg
from services.clients import bot
from services.errors import BotError
from services.models import SOURCE_TELEGRAM, Track

log = logging.getLogger(__name__)

_download_slots = asyncio.Semaphore(2)


def ensure_duration_ok(track: Track) -> None:
    limit = get_config().max_duration_minutes * 60
    if track.duration and track.duration > limit:
        raise BotError(f"That track is too long. The limit is {get_config().max_duration_minutes} minutes.")


async def resolve(track: Track) -> str:
    """Return what py-tgcalls should open: a URL, or a local file for Telegram uploads."""
    if track.source != SOURCE_TELEGRAM:
        return track.location

    if track.local_path and Path(track.local_path).is_file():
        return track.local_path

    cfg = get_config()
    cfg.download_dir.mkdir(parents=True, exist_ok=True)
    target = cfg.download_dir / f"{uuid.uuid4().hex}.media"

    async with _download_slots:
        try:
            downloaded = await bot.download_media(track.location, file_name=str(target))
        except Exception:  # noqa: BLE001
            log.warning("Telegram download failed", exc_info=True)
            raise BotError("I couldn't download that file from Telegram.") from None
    if not downloaded:
        raise BotError("I couldn't download that file from Telegram.")

    path = str(downloaded)
    try:
        info = await ffmpeg.probe(path, remote=False)
        if not track.duration:
            track.duration = int(info.duration)
        if track.is_video and not info.has_video:
            track.is_video = False
        ensure_duration_ok(track)
    except BotError:
        _remove(path)
        raise
    track.local_path = path
    return path


def _remove(path: str | None) -> None:
    if not path:
        return
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        log.debug("Could not remove %s", path, exc_info=True)


def release(track: Track) -> None:
    """Delete the downloaded copy of a track, if any."""
    if track.local_path:
        _remove(track.local_path)
        track.local_path = None


def purge_downloads() -> None:
    """Remove leftovers from a previous run (the queue is memory-only)."""
    directory = get_config().download_dir
    if not directory.is_dir():
        return
    for path in directory.iterdir():
        if path.is_file():
            _remove(str(path))


def cleanup_old_files(in_use: set[str], max_age_seconds: int) -> int:
    """Delete stale downloads that are not referenced by any queue."""
    directory = get_config().download_dir
    if not directory.is_dir():
        return 0
    removed = 0
    now = time.time()
    for path in directory.iterdir():
        try:
            if path.is_file() and str(path) not in in_use and now - path.stat().st_mtime > max_age_seconds:
                path.unlink()
                removed += 1
        except OSError:
            continue
    return removed
