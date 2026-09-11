import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# .env থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

API_URL = "http://127.0.0.1:8000/api/verify-fact"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("FactCheck AI-তে স্বাগতম! সংবাদের সত্যতা যাচাই করতে কোনো খবর বা টেক্সট দিন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # ইউজারকে জানানো যে কাজ চলছে
    processing_msg = await update.message.reply_text("🔍 তথ্য যাচাই করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    try:
        # লক্ষ্য করো: এখানে "query" এর বদলে "claim" দেওয়া হয়েছে
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"claim": user_text}, timeout=30.0)
            
        if response.status_code == 200:
            data = response.json()
            
            # টিমমেটের কোড অনুযায়ী রেজাল্ট সাজানো
            verdict = data.get("verdict", "অজানা")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            # সুন্দর করে ইউজারকে মেসেজ দেওয়া
            final_reply = (
                f"✅ **ফলাফল:** {verdict}\n"
                f"📊 **ট্রাস্ট স্কোর:** {trust_score}%\n\n"
                f"📝 **ব্যাখ্যা:** {explanation}"
            )
            
            await processing_msg.edit_text(final_reply)
        else:
            await processing_msg.edit_text("⚠️ ব্যাকএন্ড সার্ভার থেকে কোনো উত্তর পাওয়া যায়নি!")
            
    except Exception as e:
        await processing_msg.edit_text("❌ এরর: সার্ভারের সাথে কানেক্ট করা যাচ্ছে না।")

if __name__ == "__main__":
    print("Telegram Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling()