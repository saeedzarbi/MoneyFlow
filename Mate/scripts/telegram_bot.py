from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from geminitel import translate_farsi_to_english_and_turkish

TOKEN = "7999248560:AAH5Y-T1yahUNoT7emAzZoF8TD5n1bBC5lI"
AUTHORIZED_USERS = [6345123207, 987654321]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    await update.message.reply_text("Hello! The bot has started successfully.")

async def print_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(f"User ID: {user_id}")

async def test_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("You are authorized to use this bot.")
    else:
        await update.message.reply_text("You are not authorized to use this bot.")

async def translate_farsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    text = update.message.text
    if not any('\u0600' <= c <= '\u06FF' for c in text):
        await update.message.reply_text("Please send a Persian sentence.")
        return
    await update.message.reply_text("Translating your sentence...")
    try:
        result = translate_farsi_to_english_and_turkish(text)
        await update.message.reply_text(f"English translation:\n{result['english']}\n\nTurkish translation:\n{result['turkish']}")
    except Exception as e:
        print(e)
        await update.message.reply_text("Translation failed. Please try again later.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Bot commands:\n"
        "/start - Start and welcome\n"
        "/test_access - Check if you are authorized\n"
        "Send a Persian sentence - Translate to English and Turkish with Gemini\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, print_user_id), group=0)
    app.add_handler(CommandHandler("start", start), group=1)
    app.add_handler(CommandHandler("test_access", test_access), group=1)
    app.add_handler(CommandHandler("help", help_command), group=1)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_farsi), group=2)
    app.run_polling()
