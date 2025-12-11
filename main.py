import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIGURATION ==========
# Get your bot token from environment variable (safe) or paste directly
BOT_TOKEN = os.environ.get('BOT_TOKEN') or "YOUR_BOT_TOKEN_HERE"  # Change this!

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== GLOBAL WATCHLIST ==========
# This stores user IDs the bot is watching
WATCHED_USERS = set()

# ========== BOT COMMANDS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple start command"""
    await update.message.reply_text(
        "👁️ Watch Bot Active!\n\n"
        "Commands:\n"
        "/watch [user_id] - Add user to watch list\n"
        "/unwatch [user_id] - Remove user from watch list\n"
        "/list - Show watched users\n"
        "/clear - Clear all watched users"
    )

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a user to the watch list"""
    # Check if command is used in a group
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check if user is an admin
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    # Check if user ID was provided
    if not context.args:
        await update.message.reply_text("❌ Usage: /watch [user_id]\nExample: /watch 123456789")
        return
    
    try:
        user_id = int(context.args[0])
        WATCHED_USERS.add(user_id)
        await update.message.reply_text(f"✅ Added user {user_id} to watch list. All their messages will be deleted.")
        logger.info(f"Added user {user_id} to watch list by admin {update.effective_user.id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID! Must be a number.")

async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a user from the watch list"""
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /unwatch [user_id]")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in WATCHED_USERS:
            WATCHED_USERS.remove(user_id)
            await update.message.reply_text(f"✅ Removed user {user_id} from watch list.")
            logger.info(f"Removed user {user_id} from watch list")
        else:
            await update.message.reply_text(f"❌ User {user_id} is not in the watch list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all watched users"""
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    if not WATCHED_USERS:
        await update.message.reply_text("📭 Watch list is empty.")
    else:
        users_list = "\n".join([f"• {user_id}" for user_id in WATCHED_USERS])
        await update.message.reply_text(f"👁️ Watched Users:\n{users_list}")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all watched users"""
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    WATCHED_USERS.clear()
    await update.message.reply_text("✅ Cleared all watched users.")
    logger.info(f"Watch list cleared by admin {update.effective_user.id}")

# ========== MESSAGE HANDLER ==========
async def delete_watched_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete messages from watched users"""
    # Don't process if no message
    if not update.message:
        return
    
    user_id = update.effective_user.id
    
    # Check if this user is being watched
    if user_id in WATCHED_USERS:
        try:
            # Try to delete the message
            await update.message.delete()
            logger.info(f"Deleted message from watched user {user_id}")
            
            # Optional: Send a silent deletion notice (only admins see it)
            # Uncomment next 3 lines if you want this feature
            # admin_notice = f"🗑️ Deleted message from watched user: {user_id}"
            # await context.bot.send_message(
            #     chat_id=update.effective_chat.id,
            #     text=admin_notice,
            #     disable_notification=True
            # )
            
        except Exception as e:
            # If deletion fails (bot isn't admin or message already deleted)
            logger.error(f"Failed to delete message: {e}")

# ========== ERROR HANDLER ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("watch", watch_command))
    application.add_handler(CommandHandler("unwatch", unwatch_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Add message handler - this catches ALL messages
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,  # All messages except commands
        delete_watched_messages
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()