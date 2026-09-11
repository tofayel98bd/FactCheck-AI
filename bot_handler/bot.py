import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# .env থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# /start কমান্ডের রিপ্লাই
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("FactCheck AI-তে স্বাগতম! সংবাদের সত্যতা যাচাই করতে কোনো খবর, টেক্সট বা লিংক দিন।")

# সাধারণ মেসেজের রিপ্লাই
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # আপাতত এটি শুধু ডামি রিপ্লাই দেবে। পরে এখানে তোমার টিমমেটের তৈরি করা FastAPI-এর লিংক কল করা হবে।
    await update.message.reply_text(f"তুমি পাঠিয়েছো: {user_text}\n\n[এআই লজিক এখনও কানেক্ট করা হয়নি। তোমার টিমমেট ফেজ ২ শেষ করলে এটি আসল রেজাল্ট দেবে!]")

if __name__ == "__main__":
    print("Telegram Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling()