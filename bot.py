from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Replace with your actual API token from BotFather
API_TOKEN = '7380868862:AAEK3dzX9_Q9v2bgi7EVrpwc-NA81lfAJ6o'

# Dictionary to store filters in the format:
# {keyword: {"text": text, "link": link}}
filters_map = {}

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_url = "https://graph.org/file/8f0ad8a23e1ac2a980f4e-3d25103b6a7fcf256b.jpg"  # Replace with your image URL
    caption = (
        "🔰 Hello! I'm a ACX keyword filter bot.!!\n\n"
        "Use /setfilter to set a filter based on an image and links.\n"
        "Here's how:\n"
        "- Send /setfilter Keyword - Title - Link\n"
        "- Send the keyword in chat\n"
        "- I will provide the link with the keyword.\n"
        "Once set, you can use /listfilters & /removefilter to manage."
    )
    
    # Inline buttons:
    # Row 1: Let's roll
    # Row 2: Support, Channel
    # Row 3: Owner
    buttons = [
        [InlineKeyboardButton("Lᴇᴛ's Rᴏʟʟ Bᴀʙʏ", url="http://t.me/GFilterBotRobot?startgroup=botstart")],
        [
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ Cʜᴀᴛ", url="https://t.me/ACX_DISCUSSION"),
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ", url="https://t.me/ACX_NETWORK")
        ],
        [InlineKeyboardButton("Oᴡɴᴇʀ", url="https://t.me/THEHYPER_ACX")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

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
            button = InlineKeyboardButton("🔰 Wᴀᴛᴄʜ Nᴏᴡ 🔰", url=data["link"])
            reply_markup = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(
                reply_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True  # Disable link preview here
            )
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
