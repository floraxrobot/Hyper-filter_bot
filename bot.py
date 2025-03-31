from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from pymongo import MongoClient

# Replace with your actual API token from BotFather
API_TOKEN = '7380868862:AAEK3dzX9_Q9v2bgi7EVrpwc-NA81lfAJ6o'

# MongoDB configuration – replace with your own MongoDB URI if needed
MONGO_URI = "mongodb+srv://bornhyper1:Bornhyper5911@cluster0.gmvpm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your MongoDB connection string
client = MongoClient(MONGO_URI)
db = client["acx_bot"]
filters_collection = db["filters"]
users_collection = db["users"]

# Set your owner Telegram ID (only the owner can use certain commands)
OWNER_ID = 6136203777  # Replace with your actual Telegram user ID

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Save user in mongodb if not already saved
    user_id = update.effective_user.id
    users_collection.update_one({"user_id": user_id}, {"$setOnInsert": {"user_id": user_id}}, upsert=True)

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
    # Row 2: Support Chat, Support channel
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
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Expecting format: /setfilter Keyword - Title - Link
    args = update.message.text.split(" ", 1)
    if len(args) < 2:
        await update.message.reply_text("Usage: /setfilter Keyword - Title - Link")
        return

    try:
        # Split based on " - " exactly into 3 parts: Keyword, Title, and Link
        keyword, text, link = [part.strip() for part in args[1].split(" - ", 2)]
    except ValueError:
        await update.message.reply_text("Incorrect format. Please use: /setfilter Keyword - Title - Link")
        return

    keyword_lower = keyword.lower()
    filters_collection.update_one(
        {"keyword": keyword_lower},
        {"$set": {"text": text, "link": link}},
        upsert=True
    )
    await update.message.reply_text(f"Filter set for keyword '{keyword_lower}'.")


async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /removefilter <keyword>")
        return

    keyword = " ".join(context.args).strip().lower()
    result = filters_collection.delete_one({"keyword": keyword})
    if result.deleted_count:
        await update.message.reply_text(f"Filter removed for keyword '{keyword}'.")
    else:
        await update.message.reply_text("This filter does not exist.")


async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    filters_cursor = filters_collection.find()
    filters_list = [f"{doc['keyword']}: {doc['text']}" for doc in filters_cursor]
    if filters_list:
        await update.message.reply_text("Current filters:\n" + "\n".join(filters_list))
    else:
        await update.message.reply_text("No filters have been set.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    user_count = users_collection.count_documents({})
    await update.message.reply_text(f"Total users: {user_count}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    broadcast_message = update.message.text.split(" ", 1)[1]
    users = list(users_collection.find())
    success = 0
    failure = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=broadcast_message)
            success += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user['user_id']}: {e}")
            failure += 1

    await update.message.reply_text(f"Broadcast complete.\nSuccess: {success}\nFailure: {failure}")


async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    # Load all filters from MongoDB and check if any keyword exists in the message.
    for filter_doc in filters_collection.find():
        if filter_doc["keyword"] in message_text:
            # Hyperlink the text using HTML formatting
            reply_text = f'<a href="{filter_doc["link"]}">{filter_doc["text"]}</a>'
            button = InlineKeyboardButton("🔰 Wᴀᴛᴄʜ Nᴏᴡ 🔰", url=filter_doc["link"])
            reply_markup = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(
                reply_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            break  # Only respond to the first matching keyword


def main():
    application = Application.builder().token(API_TOKEN).build()

    # Commands available to everyone
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("listfilters", list_filters))
    
    # Owner-only commands
    application.add_handler(CommandHandler("setfilter", set_filter))
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Respond to any text messages that are not commands.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

    application.run_polling()


if __name__ == "__main__":
    main()
