import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# .env থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/verify-fact")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 *FactCheck AI-তে স্বাগতম!*\n\n"
        "সংবাদের সত্যতা যাচাই করতে যেকোনো খবর, পোস্ট বা টেক্সট আমাকে পাঠান।\n"
        "আমি রিয়েল-টাইমে অনলাইন সোর্স সার্চ করে প্রমাণের লিংক ও ট্রাস্ট স্কোরসহ আপনাকে ফ্যাক্ট-চেক রিপোর্ট প্রদান করব।"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # অতি সংক্ষিপ্ত মেসেজের জন্য ইউজারকে গাইড করা
    if len(user_text) < 5:
        await update.message.reply_text(
            "👋 হাই! সংবাদের সত্যতা যাচাই করতে অন্তত ৫ অক্ষরের কোনো খবরের দাবি লিখে পাঠান।\n\n"
            "📌 *উদাহরণ:* `বাংলাদেশে আগামী রবিবার ১০ দিনের সরকারি ছুটি ঘোষণা করা হয়েছে।`",
            parse_mode="Markdown"
        )
        return

    # প্রসেসিং মেসেজ দেখানো
    processing_msg = await update.message.reply_text("🔍 *তথ্য যাচাই করা হচ্ছে, একটু অপেক্ষা করুন...*", parse_mode="Markdown")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(API_URL, json={"claim": user_text, "language": "bn"})
            
        if response.status_code == 200:
            data = response.json()
            
            verdict = data.get("verdict", "অজানা")
            trust_score = data.get("trust_score", 0)
            explanation = data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।")
            sources = data.get("sources", [])

            # সুন্দর করে মার্কডাউন ফরম্যাটে ইউজারকে রেসপন্স দেওয়া
            final_reply = (
                f"🏷️ *ফলাফল:* {verdict}\n"
                f"📊 *ট্রাস্ট স্কোর:* {trust_score}%\n\n"
                f"💡 *ব্যাখ্যা:* {explanation}\n\n"
            )
            if sources:
                final_reply += "🔗 *প্রমাণের উৎস:*\n"
                for idx, s in enumerate(sources[:3], 1):
                    title = s.get("title", "সোর্স")
                    url = s.get("url", "#")
                    final_reply += f"{idx}. [{title}]({url})\n"

            await processing_msg.edit_text(final_reply, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            error_detail = response.json().get("detail", "যাচাইকরণে সমস্যা হয়েছে।")
            await processing_msg.edit_text(f"⚠️ {error_detail}")
            
    except Exception as e:
        print(f"[Bot Error] {e}")
        await processing_msg.edit_text("❌ এরর: ব্যাকএন্ড সার্ভারের সাথে কানেক্ট করা যাচ্ছে না। নিশ্চিত করুন `python main.py` চালু আছে।")

if __name__ == "__main__":
    if not TOKEN or len(TOKEN.strip()) < 10 or TOKEN.startswith("your_"):
        print("\n" + "="*60)
        print("❌ [এরর] টেলিগ্রাম বট টোকেন পাওয়া যায়নি!")
        print("="*60)
        print("বটটি চালু করতে আপনার `.env` ফাইলে একটি সঠিক Telegram Bot Token বসাতে হবে।")
        print("\n🔑 যেভাবে ১ মিনিটে টেলিগ্রাম বটের টোকেন পাবেন:")
        print("১. টেলিগ্রাম অ্যাপে গিয়ে সার্চ করুন: @BotFather (অথবা https://t.me/BotFather লিংকে যান)")
        print("২. /newbot লিখে আপনার বটের একটি নাম ও ইউজারনেম দিন।")
        print("৩. BotFather আপনাকে একটি টোকেন দেবে (যেমন: 123456789:ABCdefGHI...)")
        print("৪. প্রজেক্টের `.env` ফাইলটিতে এই লাইনটি যুক্ত করুন:")
        print("   TELEGRAM_BOT_TOKEN=আপনার_টোকেনটি_এখানে_বসাবেন")
        print("="*60 + "\n")
    else:
        print("Telegram Bot is starting...")
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Bot is running! Press Ctrl+C to stop.")
        app.run_polling()
