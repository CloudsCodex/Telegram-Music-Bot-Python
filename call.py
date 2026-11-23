# Developer by : Mr_Manas_Op
"""Thin wrapper around py-tgcalls: joining, streaming, volume and call events."""

from __future__ import annotations

import inspect
import logging

from pytgcalls import filters
from pytgcalls.types import AudioQuality, ChatUpdate, MediaStream, VideoQuality

from services.clients import calls

log = logging.getLogger(__name__)


def build_stream(source: str, video: bool, offset: float = 0.0) -> MediaStream:
    ffmpeg_params = f"-ss {int(offset)}" if offset > 0 else None
    if video:
        return MediaStream(
            source,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.SD_480p,
            ffmpeg_parameters=ffmpeg_params,
        )
    return MediaStream(
        source,
        audio_parameters=AudioQuality.HIGH,
        video_flags=MediaStream.Flags.IGNORE,
        ffmpeg_parameters=ffmpeg_params,
    )


async def start() -> None:
    await calls.start()


async def play(chat_id: int, source: str, video: bool = False, offset: float = 0.0) -> None:
    """Join the voice chat (or switch the stream if already joined) and play ``source``."""
    await calls.play(chat_id, build_stream(source, video, offset))


async def pause(chat_id: int) -> None:
    await calls.pause(chat_id)


async def resume(chat_id: int) -> None:
    await calls.resume(chat_id)


async def mute(chat_id: int) -> None:
    await calls.mute(chat_id)


async def unmute(chat_id: int) -> None:
    await calls.unmute(chat_id)


async def set_volume(chat_id: int, volume: int) -> None:
    await calls.change_volume_call(chat_id, volume)


async def leave(chat_id: int) -> None:
    await calls.leave_call(chat_id)


def register_handlers(on_stream_end, on_call_closed) -> None:
    """Attach py-tgcalls update handlers. Call once, before ``start()``.

    on_stream_end(chat_id)   -- a track finished playing.
    on_call_closed(chat_id)  -- the voice chat ended or the assistant was removed.
    """
    stream_end = filters.stream_end
    if inspect.isfunction(stream_end):
        stream_end = stream_end()

    @calls.on_update(stream_end)
    async def _stream_end(_, update):
        await on_stream_end(update.chat_id)

    try:
        status = ChatUpdate.Status
        closed = status.CLOSED_VOICE_CHAT | status.KICKED | status.LEFT_GROUP

        @calls.on_update(filters.chat_update(closed))
        async def _call_closed(_, update):
            await on_call_closed(update.chat_id)

    except Exception:  # noqa: BLE001 - optional cleanup hook
        log.warning("Voice-chat close events are not available in this py-tgcalls version.", exc_info=True)
