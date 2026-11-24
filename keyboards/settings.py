# Developer by : Mr_Manas_Op
"""Settings panel text and keyboard."""

from __future__ import annotations

from typing import Any

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from helpers.cards import loop_label


def settings_text(settings: dict[str, Any]) -> str:
    controls = "Admins only" if settings["controls_mode"] == "admins" else "Everyone"
    announce = "On" if settings["announce"] else "Off"
    return (
        "⚙️ <b>Music settings</b>\n\n"
        f"🎚 Playback controls: <b>{controls}</b>\n"
        f"🔊 Default volume: <b>{settings['volume']}%</b>\n"
        f"🔁 Loop mode: <b>{loop_label(settings['loop_mode'])}</b>\n"
        f"📢 Now-playing announcements: <b>{announce}</b>\n\n"
        "Only group admins can change these options."
    )


def settings_markup(settings: dict[str, Any]) -> InlineKeyboardMarkup:
    controls = "Admins only" if settings["controls_mode"] == "admins" else "Everyone"
    announce = "On" if settings["announce"] else "Off"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"🎚 Controls: {controls}", callback_data="st|ctl")],
            [
                InlineKeyboardButton("🔉 Volume −10", callback_data="st|vdn"),
                InlineKeyboardButton("🔊 Volume +10", callback_data="st|vup"),
            ],
            [InlineKeyboardButton(f"🔁 Loop: {loop_label(settings['loop_mode'])}", callback_data="st|loop")],
            [InlineKeyboardButton(f"📢 Announcements: {announce}", callback_data="st|ann")],
            [InlineKeyboardButton("✖ Close", callback_data="st|close")],
        ]
    )
