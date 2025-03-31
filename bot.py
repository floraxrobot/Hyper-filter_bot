from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging

# Replace 'YOUR_API_TOKEN' with the actual token from BotFather
API_TOKEN = '7163289613:AAEZaSCRfujwcA387HiLx3E50EymwTi4amI'

# Dictionary to store media filters in the format: {keyword: {"image": file_id, "title": title, "links": [(label, url), ...]}}
media_filters = {}

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_TITLE, WAITING_FOR_LINKS = range(2)

# Start command with image and inline buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_url = "https://i.ibb.co/NS8hdGZ/file-1157.jpg"  # Replace with your image URL
    caption = (
        "Hello! I'm a media-based keyword filter bot.👋🏻\n\nUse /setmedia to set a filter based on an image and "
        "links.\nHere's how:\n"
        "- Reply to an image with /setmedia\n"
        "- Provide a title when prompted\n"
        "- Provide labeled links in the format `Label - Link, Label - Link` when prompted\n"
        "Once set, typing the keyword will display the image, title, and links."
    )
    
    # Inline buttons setup
    buttons = [
        [InlineKeyboardButton("➕Let's Roll ➕", url="http://t.me/HYPERXMUSICROBOT?startgroup=botstart")],
        [
            InlineKeyboardButton("Support", url="https://t.me/ACX_DISCUSSION"),
            InlineKeyboardButton("Chat", url="https://t.me/ACX_NETWORK")
        ],
        [InlineKeyboardButton("Owner 🧑🏻‍💻", url="https://t.me/THEHYPER_ACX")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        reply_markup=reply_markup
    )

# Set a new media filter
async def set_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        context.user_data["image"] = update.message.reply_to_message.photo[-1].file_id
        await update.message.reply_text("Please provide a title for the image:")
        return WAITING_FOR_TITLE
    else:
        await update.message.reply_text("Please reply to an image with /setmedia.")
        return ConversationHandler.END

# Receive title
async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Now, please provide the links in the format `Label - Link, Label - Link`.")
    return WAITING_FOR_LINKS

# Receive links and save the filter
async def receive_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    links_text = update.message.text
    links = []

    try:
        for item in links_text.split(","):
            label, url = item.split(" - ", 1)
            links.append((label.strip(), url.strip()))
        
        keyword = context.user_data["title"].lower()
        media_filters[keyword] = {
            "image": context.user_data["image"],
            "title": context.user_data["title"],
            "links": links
        }
        
        await update.message.reply_text(f"Media filter set for keyword '{context.user_data['title']}'!")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please use the correct format: Label - Link, Label - Link")
        return WAITING_FOR_LINKS

# Remove a filter
async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Get the keyword argument, lowercase it and strip extra spaces
        keyword = " ".join(context.args).strip().lower()  # Join in case keyword has spaces

        if keyword in media_filters:
            del media_filters[keyword]
            await update.message.reply_text(f"Filter removed for keyword '{keyword}'.")
        else:
            await update.message.reply_text("This filter does not exist.")
    except IndexError:
        await update.message.reply_text("Usage: /removefilter <keyword>")

# List all filters
async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if media_filters:
        filters_list = "\n".join([f"{data['title']}" for data in media_filters.values()])
        await update.message.reply_text(f"Current filters are -\n{filters_list}")
    else:
        await update.message.reply_text("No filters have been set.")

# Respond to a keyword with an image, title, and links
async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    for keyword, data in media_filters.items():
        if keyword in message_text:
            formatted_caption = f"🔰 {data['title']} ⤵️⤵️"
            buttons = [[InlineKeyboardButton(text=label, url=url)] for label, url in data["links"]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_photo(
                photo=data["image"],
                caption=formatted_caption,
                reply_markup=reply_markup
            )
            break

# Cancel command for conversation handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to set up the bot
def main():
    application = Application.builder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setmedia", set_media)],
        states={
            WAITING_FOR_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            WAITING_FOR_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_links)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("listfilters", list_filters))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

    application.run_polling()

if __name__ == "__main__":
    main()
