import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN') or "YOUR_BOT_TOKEN_HERE"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== GLOBAL WATCHLIST ==========
WATCHED_USERS = set()

# ========== BOT COMMANDS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👁️ Watch Bot Active!\n\n"
        "Commands:\n"
        "/watch [user_id] - Add user to watch list\n"
        "/unwatch [user_id] - Remove user from watch list\n"
        "/list - Show watched users\n"
        "/clear - Clear all watched users"
    )

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    try:
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Only admins can use this command!")
            return
    except:
        await update.message.reply_text("❌ Could not verify admin status!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /watch [user_id]\nExample: /watch 123456789")
        return
    
    try:
        user_id = int(context.args[0])
        WATCHED_USERS.add(user_id)
        await update.message.reply_text(f"✅ Added user {user_id} to watch list.")
        logger.info(f"Added user {user_id} to watch list")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID! Must be a number.")

async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /unwatch [user_id]")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in WATCHED_USERS:
            WATCHED_USERS.remove(user_id)
            await update.message.reply_text(f"✅ Removed user {user_id} from watch list.")
        else:
            await update.message.reply_text(f"❌ User {user_id} is not in the watch list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not WATCHED_USERS:
        await update.message.reply_text("📭 Watch list is empty.")
    else:
        users_list = "\n".join([f"• {user_id}" for user_id in WATCHED_USERS])
        await update.message.reply_text(f"👁️ Watched Users:\n{users_list}")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    WATCHED_USERS.clear()
    await update.message.reply_text("✅ Cleared all watched users.")
    logger.info("Watch list cleared")

# ========== MESSAGE HANDLER ==========
async def delete_watched_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    user_id = update.effective_user.id
    
    if user_id in WATCHED_USERS:
        try:
            await update.message.delete()
            logger.info(f"Deleted message from watched user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")

# ========== ERROR HANDLER ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot"""
    print("🤖 Bot is starting...")
    print(f"Token present: {'YES' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'NO'}")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set BOT_TOKEN as environment variable on Render!")
        print("Go to your Render dashboard → Environment → Add BOT_TOKEN")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("watch", watch_command))
    application.add_handler(CommandHandler("unwatch", unwatch_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Add message handler
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        delete_watched_messages
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    print("✅ Bot configured. Starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
