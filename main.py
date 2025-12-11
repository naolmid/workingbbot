import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ========== CONFIGURATION ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== GLOBAL WATCHLIST ==========
WATCHED_USERS = set()

# ========== BOT COMMANDS ==========
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👁️ Watch Bot Active!\n\n"
        "Commands:\n"
        "/watch [user_id] - Add user to watch list\n"
        "/unwatch [user_id] - Remove user\n"
        "/list - Show watched users\n"
        "/clear - Clear all"
    )

def watch(update: Update, context: CallbackContext):
    if update.effective_chat.type not in ["group", "supergroup"]:
        update.message.reply_text("❌ Group only!")
        return
    
    if not context.args:
        update.message.reply_text("❌ Use: /watch 123456789")
        return
    
    try:
        user_id = int(context.args[0])
        WATCHED_USERS.add(user_id)
        update.message.reply_text(f"✅ Added {user_id}")
    except:
        update.message.reply_text("❌ Invalid ID!")

def unwatch(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /unwatch 123456789")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in WATCHED_USERS:
            WATCHED_USERS.remove(user_id)
            update.message.reply_text(f"✅ Removed {user_id}")
        else:
            update.message.reply_text(f"❌ Not in list")
    except:
        update.message.reply_text("❌ Invalid ID!")

def list_users(update: Update, context: CallbackContext):
    if not WATCHED_USERS:
        update.message.reply_text("📭 Empty")
    else:
        users = "\n".join([f"• {uid}" for uid in WATCHED_USERS])
        update.message.reply_text(f"👁️ Watching:\n{users}")

def clear(update: Update, context: CallbackContext):
    WATCHED_USERS.clear()
    update.message.reply_text("✅ Cleared all")

# ========== MESSAGE HANDLER ==========
def delete_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if user_id in WATCHED_USERS:
        try:
            update.message.delete()
            logger.info(f"Deleted message from {user_id}")
        except:
            logger.error("Failed to delete")

# ========== MAIN ==========
def main():
    print("🤖 Starting bot...")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Set BOT_TOKEN on Render!")
        return
    
    # Use Updater class (compatible with 20.7)
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("watch", watch))
    dispatcher.add_handler(CommandHandler("unwatch", unwatch))
    dispatcher.add_handler(CommandHandler("list", list_users))
    dispatcher.add_handler(CommandHandler("clear", clear))
    
    # Add message handler (all messages except commands)
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, 
        delete_message
    ))
    
    print("✅ Bot configured. Starting...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
