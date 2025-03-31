from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Replace with your actual API token from BotFather
API_TOKEN = '7380868862:AAE6n_0npHSPcQsAj7ar2tK4JLNQsfSuIVk'

# Dictionary to store filters in the format:
# {keyword: {"text": text, "link": link}}
filters_map = {}

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Hello! I'm a simple filter bot.\n\n"
        "Use the command /setfilter in the following format:\n"
        "/setfilter Keyword - Text - Link\n\n"
        "When someone sends a message that contains the keyword, I'll respond with the Text "
        "hyperlinked to the provided Link and include a 'Download' button."
    )
    await update.message.reply_text(message)

async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Expecting format: /setfilter Keyword - Text - Link
    args = update.message.text.split(" ", 1)
    if len(args) < 2:
        await update.message.reply_text("Usage: /setfilter Keyword - Text - Link")
        return

    try:
        # Split based on " - " exactly into 3 parts: Keyword, Text, and Link
        keyword, text, link = [part.strip() for part in args[1].split(" - ", 2)]
    except ValueError:
        await update.message.reply_text("Incorrect format. Please use: /setfilter Keyword - Text - Link")
        return

    keyword_lower = keyword.lower()
    filters_map[keyword_lower] = {"text": text, "link": link}
    await update.message.reply_text(f"Filter set for keyword '{keyword_lower}'.")

async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /removefilter <keyword>")
        return

    keyword = " ".join(context.args).strip().lower()
    if keyword in filters_map:
        del filters_map[keyword]
        await update.message.reply_text(f"Filter removed for keyword '{keyword}'.")
    else:
        await update.message.reply_text("This filter does not exist.")

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if filters_map:
        filters_list = "\n".join([f"{k}: {data['text']}" for k, data in filters_map.items()])
        await update.message.reply_text(f"Current filters:\n{filters_list}")
    else:
        await update.message.reply_text("No filters have been set.")

async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    # Check each filter keyword; if found, respond with its text hyperlinked and a button.
    for keyword, data in filters_map.items():
        if keyword in message_text:
            # Hyperlink the text using HTML formatting
            reply_text = f'<a href="{data["link"]}">{data["text"]}</a>'
            button = InlineKeyboardButton("Download", url=data["link"])
            reply_markup = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(reply_text, reply_markup=reply_markup, parse_mode="HTML")
            break  # Only respond to the first matching keyword

def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setfilter", set_filter))
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("listfilters", list_filters))
    # Replies to any text messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

    application.run_polling()

if __name__ == "__main__":
    main()
