import os
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
from models.english_word import WordType, WordLevel
from models.telegram_bot import TelegramUser

load_dotenv()

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _get_bot_token():
    return os.getenv("TELEGRAM_BOT_TOKEN")


def _get_chat_ids():
    """Collect chat IDs from DB users and optional TELEGRAM_CHAT_IDS env."""
    chat_ids = set()

    try:
        for user in TelegramUser.query.all():
            if user.user_id:
                chat_ids.add(str(user.user_id))
    except Exception as e:
        print(f"Error loading Telegram users from DB: {e}")

    env_ids = os.getenv("TELEGRAM_CHAT_IDS", "")
    for chat_id in env_ids.split(","):
        chat_id = chat_id.strip()
        if chat_id:
            chat_ids.add(chat_id)

    return list(chat_ids)


TELEGRAM_MAX_LENGTH = 4000


def _chunk_message(message, max_length=TELEGRAM_MAX_LENGTH):
    if len(message) <= max_length:
        return [message]

    chunks = []
    current = ""
    for part in message.split("\n"):
        candidate = f"{current}\n{part}" if current else part
        if len(candidate) > max_length:
            if current:
                chunks.append(current)
            while len(part) > max_length:
                chunks.append(part[:max_length])
                part = part[max_length:]
            current = part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def _send_to_chat(token, chat_id, message):
    ok = True
    for chunk in _chunk_message(message):
        response = requests.post(
            TELEGRAM_API.format(token=token),
            json={
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if response.status_code != 200:
            print(
                f"Error sending Telegram message to {chat_id}: "
                f"{response.status_code} - {response.text}"
            )
            ok = False
    return ok


def send_telegram_notification(message):
    """Send a plain-text notification to all registered Telegram chats."""
    token = _get_bot_token()
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN is not set")
        return False

    chat_ids = _get_chat_ids()
    if not chat_ids:
        print("Error: no Telegram chat IDs configured")
        return False

    success = False
    for chat_id in chat_ids:
        try:
            if _send_to_chat(token, chat_id, message):
                success = True
        except Exception as e:
            print(f"Error sending Telegram notification to {chat_id}: {e}")

    return success


def send_daily_words_to_telegram(words):
    """Format and send daily English words via Telegram."""
    try:
        if not words:
            return False

        tehran_tz = pytz.timezone("Asia/Tehran")
        today = datetime.now(tehran_tz).strftime("%Y-%m-%d")

        message_text = f"✨ 📚 Daily English Words - {today} ✨\n"
        message_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, word in enumerate(words, 1):
            word_text = getattr(word, "word", None) or word.get("word")
            translation = getattr(word, "translation", None) or word.get("translation")
            word_type = getattr(word, "type", None) or word.get("type")
            level = getattr(word, "level", None) or word.get("level")
            note = getattr(word, "note", None)
            if note is None and isinstance(word, dict):
                note = word.get("note")

            type_value = word_type.value if hasattr(word_type, "value") else word_type
            level_value = level.value if hasattr(level, "value") else level

            type_emoji = {
                WordType.NOUN: "📝",
                WordType.VERB: "⚡",
                WordType.ADJECTIVE: "🌈",
                WordType.ADVERB: "🎭",
                WordType.PRONOUN: "💬",
                WordType.OTHER: "💬",
                "noun": "📝",
                "verb": "⚡",
                "adjective": "🌈",
                "adverb": "🎭",
                "pronoun": "💬",
                "other": "💬",
            }.get(word_type if hasattr(word_type, "value") else str(type_value).lower(), "📌")

            level_emoji = {
                WordLevel.A1: "🌱",
                WordLevel.A2: "🌱",
                WordLevel.B1: "🌿",
                WordLevel.B2: "🌿",
                WordLevel.C1: "🌳",
                WordLevel.C2: "🌳",
                "A1": "🌱",
                "A2": "🌱",
                "B1": "🌿",
                "B2": "🌿",
                "C1": "🌳",
                "C2": "🌳",
            }.get(level if hasattr(level, "value") else str(level_value), "📊")

            message_text += f"{i}. 🎯 {word_text}\n"
            message_text += f"   📖 Translation: {translation}\n"
            message_text += f"   {type_emoji} Type: {type_value}\n"
            message_text += f"   {level_emoji} Level: {level_value}\n"
            if note:
                message_text += f"   💡 Note: {note}\n"
            message_text += "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        message_text += "🌟 Keep learning and growing! 🌟"
        return send_telegram_notification(message_text)

    except Exception as e:
        print(f"Error sending daily words to Telegram: {e}")
        return False
