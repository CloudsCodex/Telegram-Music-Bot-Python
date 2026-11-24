# Developer by : Mr_Manas_Op
"""Inline keyboard for search results."""

from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def search_markup(token: str, count: int) -> InlineKeyboardMarkup:
    numbers = [
        InlineKeyboardButton(str(i + 1), callback_data=f"sr|{token}|{i}") for i in range(count)
    ]
    return InlineKeyboardMarkup([numbers, [InlineKeyboardButton("✖ Close", callback_data=f"sr|{token}|x")]])
