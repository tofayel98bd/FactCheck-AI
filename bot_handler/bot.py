import os
import httpx
import io
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# .env থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ব্যাকএন্ডের দুটি আলাদা API URL
API_URL_TEXT = "http://127.0.0.1:8000/api/verify-fact"
API_URL_IMAGE = "http://127.0.0.1:8000/api/verify-image"

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
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
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

# 🔹 নতুন যুক্ত করা ফাংশন: ছবি রিসিভ ও প্রসেস করা
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processing_msg = await update.message.reply_text("📸 ছবি বিশ্লেষণ করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    try:
        # টেলিগ্রাম থেকে সবচেয়ে ভালো রেজুলেশনের ছবিটি নেওয়া ([-1] মানে সবচেয়ে বড় সাইজ)
        photo_file = await update.message.photo[-1].get_file()
        
        # ছবিটিকে মেমরিতে বাইট (bytes) হিসেবে ডাউনলোড করা
        image_bytes = await photo_file.download_as_bytearray()
        
        # বাইট ডেটাকে একটি ভার্চুয়াল ফাইলে (file-like object) রূপান্তর করা
        image_stream = io.BytesIO(image_bytes)
        
        # ব্যাকএন্ডে ছবিটি পাঠানো
        async with httpx.AsyncClient() as client:
            # File পাঠানোর জন্য 'files' প্যারামিটার ব্যবহার করতে হয়
            files = {'file': ('image.jpg', image_stream, 'image/jpeg')}
            response = await client.post(API_URL_IMAGE, files=files, timeout=30.0)
            
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "অজানা")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            
            final_reply = (
                f"🔍 **ছবি বিশ্লেষণ ফলাফল:**\n\n"
                f"✅ **রায়:** {verdict}\n"
                f"📊 **ট্রাস্ট স্কোর:** {trust_score}%\n\n"
                f"📝 **ব্যাখ্যা:** {explanation}"
            )
            await processing_msg.edit_text(final_reply)
        else:
            await processing_msg.edit_text("⚠️ ব্যাকএন্ড সার্ভার ছবিটি প্রসেস করতে পারেনি!")
            
    except Exception as e:
        print(f"Bot Image Error: {e}")
        await processing_msg.edit_text("❌ এরর: সার্ভারের সাথে কানেক্ট করা যাচ্ছে না বা ছবিটি পড়া যাচ্ছে না।")

if __name__ == "__main__":
    print("Telegram Bot is starting...")
    # 🔹 টাইম-আউট লিমিট বাড়িয়ে দেওয়া হয়েছে
    app = Application.builder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is running! Press Ctrl+C to stop.")
    # 🔹 বকেয়া বা আটকে থাকা মেসেজ ড্রপ করে ফ্রেশ স্টার্ট করবে
    app.run_polling(drop_pending_updates=True)