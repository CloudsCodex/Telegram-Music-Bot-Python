# Developer by : Mr_Manas_Op
"""Error notifications. Technical details go to bot owners only, never to users."""

from __future__ import annotations

import logging
import time
import traceback

from config import get_config
from helpers.formatting import esc
from services.clients import bot

log = logging.getLogger(__name__)

_THROTTLE_SECONDS = 60
_last_sent: dict[str, float] = {}


async def notify_owners(context: str, exc: BaseException) -> None:
    owners = get_config().owner_ids
    if not owners:
        return
    key = f"{type(exc).__name__}:{context}"
    now = time.monotonic()
    if now - _last_sent.get(key, 0.0) < _THROTTLE_SECONDS:
        return
    _last_sent[key] = now

    summary = "".join(traceback.format_exception_only(type(exc), exc)).strip()[-800:]
    text = f"⚠️ <b>Error</b> in <code>{esc(context)}</code>\n<code>{esc(summary)}</code>"
    for owner_id in owners:
        try:
            await bot.send_message(owner_id, text)
        except Exception:  # noqa: BLE001 - owner may not have started the bot
            log.debug("Could not notify owner %s", owner_id)
