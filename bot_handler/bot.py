import os
import httpx
import io
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# .env থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Render-এর লাইভ URL অথবা লোকাল URL সেট করা
# .env ফাইলে BACKEND_URL=https://your-app.onrender.com সেট করতে পারো
BASE_URL = os.getenv("BACKEND_URL", f"http://127.0.0.1:{os.getenv('PORT', '8000')}")
API_URL_TEXT = f"{BASE_URL.rstrip('/')}/api/verify-fact"
API_URL_IMAGE = f"{BASE_URL.rstrip('/')}/api/verify-image"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 *FactCheck-AI তে স্বাগতম!*\n\n"
        "যে কোনো খবরের সত্যতা যাচাই করতে আমাকে মেসেজ করুন।\n"
        "👉 আপনি চাইলে কোনো সংবাদ লিখে বা খবরের ছবি পাঠিয়ে চেক করতে পারেন।"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    processing_msg = await update.message.reply_text("🔍 *তথ্য যাচাই করা হচ্ছে, একটু অপেক্ষা করুন...*", parse_mode="Markdown")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL_TEXT, json={"claim": user_text}, timeout=40.0)
            
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "অনিশ্চিত")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            # ইমোজি সেট করা
            verdict_icon = "✅" if "সত্য" in verdict or "True" in verdict else "❌" if "মিথ্যা" in verdict or "Fake" in verdict else "⚠️"
            
            final_reply = (
                f"{verdict_icon} *ফলাফল:* {verdict}\n"
                f"📊 *নির্ভরযোগ্যতা (Trust Score):* {trust_score}%\n\n"
                f"📝 *ব্যাখ্যা:*\n{explanation}"
            )
            await processing_msg.edit_text(final_reply, parse_mode="Markdown")
        else:
            await processing_msg.edit_text(f"⚠️ সার্ভার এরর: {response.status_code}")
            
    except Exception as e:
        print(f"Text Handle Error: {e}")
        await processing_msg.edit_text("❌ সার্ভারের সাথে কানেক্ট করা যাচ্ছে না। কিছুক্ষণ পর আবার চেষ্টা করুন।")

# 🔹 ছবি রিসিভ ও প্রসেস করা
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processing_msg = await update.message.reply_text("📸 *ছবি বিশ্লেষণ করা হচ্ছে, একটু অপেক্ষা করুন...*", parse_mode="Markdown")
    
    try:
        # টেলিগ্রাম থেকে সবচেয়ে ভালো রেজুলেশনের ছবিটি নেওয়া
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image_stream = io.BytesIO(image_bytes)
        
        # ব্যাকএন্ডে ছবিটি পাঠানো
        async with httpx.AsyncClient() as client:
            files = {'file': ('image.jpg', image_stream, 'image/jpeg')}
            response = await client.post(API_URL_IMAGE, files=files, timeout=45.0)
            
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "অনিশ্চিত")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            verdict_icon = "✅" if "সত্য" in verdict or "True" in verdict else "❌" if "মিথ্যা" in verdict or "Fake" in verdict else "⚠️"
            
            final_reply = (
                f"🔍 *ছবি বিশ্লেষণ ফলাফল:*\n\n"
                f"{verdict_icon} *রায়:* {verdict}\n"
                f"📊 *নির্ভরযোগ্যতা (Trust Score):* {trust_score}%\n\n"
                f"📝 *ব্যাখ্যা:*\n{explanation}"
            )
            await processing_msg.edit_text(final_reply, parse_mode="Markdown")
        else:
            await processing_msg.edit_text(f"⚠️ ইমেজ সার্ভার এরর: {response.status_code}")
            
    except Exception as e:
        print(f"Bot Image Error: {e}")
        await processing_msg.edit_text("❌ ছবি যাচাইয়ের সময় সার্ভারে সমস্যা হয়েছে।")

def run_bot():
    """এই ফাংশনটি FastAPI (main.py) থেকে থ্রেডের মাধ্যমে কল করা হবে"""
    if not TOKEN or TOKEN.startswith("your_"):
        print("⚠️ Telegram Bot Token is missing or invalid! Bot will not start.")
        return

    try:
        print("Telegram bot is starting in the background...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # টাইম-আউট লিমিট বাড়িয়ে দেওয়া হয়েছে
        app = Application.builder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        print("Bot is running! Press Ctrl+C to stop.")
        app.run_polling(drop_pending_updates=True, stop_signals=None)
    except Exception as e:
        print(f"Bot Background Error: {e}")

if __name__ == "__main__":
    run_bot()