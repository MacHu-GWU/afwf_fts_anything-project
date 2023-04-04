# -*- coding: utf-8 -*-

"""
Enumerate useful, UTF8 emoji characters.

Full list is here: https://unicode.org/emoji/charts/full-emoji-list.html
"""

import enum


class Emoji(str, enum.Enum):
    start_timer = "⏱"
    end_timer = "⏰"
    go = "▶️"
    stop = "⏹️"
    error = "🔥"

    relax = "🌴"
    python = "🐍"

    test = "🧪"
    install = "💾"
    build = "🪜"
    deploy = "🚀️"
    delete = "🗑️"
    tada = "🎉"

    cloudformation = "☁️"
    awslambda = "🟧"

    template = "📋"
    computer = "💻"
    package = "📦"

    factory = "🏭"
    no_entry = "🚫"
    warning = "⚠️"

    thumb_up = "👍"
    thumb_down = "👎"
    attention = "👉"

    happy_face = "😀"
    hot_face = "🥵"
    anger = "💢"

    red_circle = "🔴"
    green_circle = "🟢"
    yellow_circle = "🟡"
    blue_circle = "🔵"

    red_square = "🟥"
    green_square = "🟩"
    yellow_square = "🟨"
    blue_square = "🟦"

    succeeded = "✅"
    failed = "❌"

    arrow_up = "⬆️"
    arrow_down = "⬇️"
    arrow_left = "⬅️"
    arrow_right = "➡️"
