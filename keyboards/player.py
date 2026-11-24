# Developer by : Mr_Manas_Op
"""Inline controls shown under the now-playing message."""

from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def player_markup(chat_id: int) -> InlineKeyboardMarkup:
    def button(label: str, action: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(label, callback_data=f"mc|{action}|{chat_id}")

    return InlineKeyboardMarkup(
        [
            [button("⏯ Pause/Resume", "pp"), button("⏭ Skip", "skip"), button("⏹ End", "end")],
            [button("🔁 Loop", "loop"), button("🔀 Shuffle", "shuffle"), button("📜 Queue", "queue")],
        ]
    )
