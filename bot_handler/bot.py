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

# Render-এ পোর্ট ডাইনামিক হয়, তাই PORT ভেরিয়েবল থেকে পোর্ট নেওয়া হচ্ছে (ডিফল্ট 8000)
PORT = os.getenv("PORT", "8000")
API_URL_TEXT = f"http://127.0.0.1:{PORT}/api/verify-fact"
API_URL_IMAGE = f"http://127.0.0.1:{PORT}/api/verify-image"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("FactCheck AI-তে স্বাগতম! সংবাদের সত্যতা যাচাই করতে কোনো টেক্সট বা ছবি (Image) পাঠান।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    processing_msg = await update.message.reply_text("🔍 তথ্য যাচাই করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL_TEXT, json={"claim": user_text}, timeout=30.0)
            
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "অজানা")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            final_reply = (
                f"✅ **ফলাফল:** {verdict}\n"
                f"📊 **ট্রাস্ট স্কোর:** {trust_score}%\n\n"
                f"📝 **ব্যাখ্যা:** {explanation}"
            )
            await processing_msg.edit_text(final_reply)
        else:
            await processing_msg.edit_text("⚠️ ব্যাকএন্ড সার্ভার থেকে কোনো উত্তর পাওয়া যায়নি!")
            
    except Exception as e:
        print(f"Text Handle Error: {e}")
        await processing_msg.edit_text("❌ এরর: সার্ভারের সাথে কানেক্ট করা যাচ্ছে না।")

# 🔹 ছবি রিসিভ ও প্রসেস করা
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processing_msg = await update.message.reply_text("📸 ছবি বিশ্লেষণ করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    try:
        # টেলিগ্রাম থেকে সবচেয়ে ভালো রেজুলেশনের ছবিটি নেওয়া
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image_stream = io.BytesIO(image_bytes)
        
        # ব্যাকএন্ডে ছবিটি পাঠানো
        async with httpx.AsyncClient() as client:
            files = {'file': ('image.jpg', image_stream, 'image/jpeg')}
            response = await client.post(API_URL_IMAGE, files=files, timeout=30.0)
            
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "অজানা")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            final_reply = (
                f"🔍 **ছবি বিশ্লেষণ ফলাফল:**\n\n"
                f"✅ **রায়:** {verdict}\n"
                f"📊 **ট্রাস্ট স্কোর:** {trust_score}%\n\n"
                f"📝 **ব্যাখ্যা:** {explanation}"
            )
            await processing_msg.edit_text(final_reply)
        else:
            await processing_msg.edit_text("⚠️ ব্যাকএন্ড সার্ভার ছবিটি প্রসেস করতে পারেনি!")
            
    except Exception as e:
        print(f"Bot Image Error: {e}")
        await processing_msg.edit_text("❌ এরর: সার্ভারের সাথে কানেক্ট করা যাচ্ছে না বা ছবিটি পড়া যাচ্ছে না।")

def run_bot():
    """এই ফাংশনটি FastAPI (main.py) থেকে থ্রেডের মাধ্যমে কল করা হবে"""
    if not TOKEN or TOKEN.startswith("your_"):
        print("⚠️ Telegram Bot Token is missing or invalid! Bot will not start.")
        return

    try:
        print("Telegram bot is starting in the background...")
        # ব্যাকগ্রাউন্ড থ্রেডে ইভেন্ট লুপ ক্র্যাশ ঠেকানোর জন্য নতুন লুপ তৈরি
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # টাইম-আউট লিমিট বাড়িয়ে দেওয়া হয়েছে
        app = Application.builder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        print("Bot is running! Press Ctrl+C to stop.")
        # বকেয়া বা আটকে থাকা মেসেজ ড্রপ করে ফ্রেশ স্টার্ট করবে
        app.run_polling(drop_pending_updates=True, stop_signals=None)
    except Exception as e:
        print(f"Bot Background Error: {e}")

if __name__ == "__main__":
    # যদি কেউ ম্যানুয়ালি শুধু এই ফাইলটি রান করে, তখন কাজ করার জন্য
    run_bot()