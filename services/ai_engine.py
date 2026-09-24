import os
import json
import httpx
import base64
from typing import List
from models.schemas import VerdictEnum, SourceItem, FactCheckResponse
from datetime import datetime

async def analyze_claim_with_rag(claim: str, sources: List[SourceItem], language: str = "bn") -> tuple[VerdictEnum, int, str]:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    current_date = datetime.now().strftime("%Y-%m-%d")

    evidence_text = "\n".join([
        f"- উৎস {idx}: {s.title}\n  ইউআরএল: {s.url}\n  সারাংশ: {s.snippet}"
        for idx, s in enumerate(sources, 1)
    ]) if sources else "কোন তথ্যসূত্র পাওয়া যায়নি।"

    prompt = f"""
আপনি একজন নিরপেক্ষ ও দক্ষ ফ্যাক্ট-চেকার। আজ {current_date}। নিচে একটি দাবি এবং ভেরিফায়েড সোর্স থেকে প্রাপ্ত তথ্য দেওয়া হলো।

[যাচাইয়ের দাবি]: "{claim}"

[ভেরিফায়েড তথ্যপ্রমাণ (RAG Evidence)]:
{evidence_text}

[আপনার কাজ ও কঠোর নির্দেশ (STRICT RULES)]:
১. শুধুমাত্র দেওয়া তথ্যপ্রমাণের ভিত্তিতে উত্তর দিন। নিজে থেকে কিছু বানাবেন গঠন করবেন না।
২. সময় যাচাই (Time-matching): 
   - ইউজারের দাবিতে যদি কোনো তারিখ বা সময় (যেমন: আজ, গতকাল, অমুক তারিখ) উল্লেখ থাকে, তবে সোর্সে থাকা আসল ঘটনার তারিখের সাথে সেটি মেলান।
   - ঘটনাটি যদি পুরোনো হয় কিন্তু ইউজার একে "আজকের" বা "সাম্প্রতিক" বলে দাবি করে, তবে একে "বিভ্রান্তিকর (Misleading)" লেবেল দিন এবং আসল তারিখটি জানিয়ে দিন। 
   - যদি ইউজারের দাবিতে কোনো সময় বা তারিখ উল্লেখ না থাকে, তবে ব্যাখ্যায় অবশ্যই জানিয়ে দিন ঘটনাটি আসলে কবে ঘটেছিল।
৩. যদি তথ্যপ্রমাণে দাবিটি পুরোপুরি মিথ্যা প্রমাণিত হয়, তবে "মিথ্যা (Fake)" দিন।
৪. যদি পর্যাপ্ত তথ্য না পাওয়া যায়, তবে "অনিশ্চিত (Unverified)" দিন।

আউটপুট অবশ্যই নিচের JSON ফরম্যাটে দিন:
{{
  "verdict": "সত্য (True)" | "মিথ্যা (Fake)" | "বিভ্রান্তিকর (Misleading)" | "অনিশ্চিত (Unverified)",
  "trust_score": 0 থেকে 100,
  "explanation": "১-৩ বাক্যে ব্যাখ্যা। তারিখের অমিল থাকলে বা ঘটনাটি পুরোনো হলে অবশ্যই আসল তারিখ উল্লেখ করবেন। সোর্সের নাম যুক্ত করবেন।"
}}
    """

    if gemini_key and not gemini_key.startswith("your_"):
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
        
        try:
            from google import genai
            from google.genai import types
            ai_client = genai.Client(api_key=gemini_key)
            for model_name in models_to_try:
                try:
                    res = ai_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    if res and res.text:
                        parsed = json.loads(res.text)
                        return parse_verdict(parsed.get("verdict", "")), int(parsed.get("trust_score", 0)), parsed.get("explanation", "")
                except Exception as e:
                    print(f"❌ SDK Error ({model_name}): {e}")
        except Exception as e:
            print(f"⚠️ SDK Import Error: {e}")

        async with httpx.AsyncClient() as client:
            for model_name in models_to_try:
                try:
                    res = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}",
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"response_mime_type": "application/json"}
                        }, timeout=30.0
                    )
                    if res.status_code == 200:
                        parsed = json.loads(res.json()["candidates"][0]["content"]["parts"][0]["text"])
                        return parse_verdict(parsed.get("verdict", "")), int(parsed.get("trust_score", 0)), parsed.get("explanation", "")
                    else:
                        print(f"❌ HTTP Response Error ({model_name}): {res.status_code} - {res.text}")
                except Exception as e:
                    print(f"❌ HTTP Connection Error ({model_name}): {e}")

    return VerdictEnum.UNVERIFIED, 50, "API Key ঠিক আছে, কিন্তু এআই মডেলের সাথে কানেক্ট করা যায়নি অথবা সার্ভার ব্যস্ত আছে।"

def parse_verdict(val: str) -> VerdictEnum:
    if "সত্য" in val or "True" in val: return VerdictEnum.TRUE
    elif "মিথ্যা" in val or "Fake" in val: return VerdictEnum.FAKE
    elif "বিভ্রান্তিকর" in val or "Misleading" in val: return VerdictEnum.MISLEADING
    else: return VerdictEnum.UNVERIFIED

async def analyze_image_with_ai(image_bytes: bytes) -> tuple[VerdictEnum, int, str]:
    """
    ছবি বিশ্লেষণ করে রিভার্স ইমেজ সার্চ, আউট-অফ-কনটেক্সট এবং এআই জেনারেটেড কি না তা যাচাই করার ফাংশন।
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    
    prompt = """
    আপনি একজন সাইবার ফরেনসিক এবং রিভার্স ইমেজ সার্চ এক্সপার্ট। 
    আপনার কাজ হলো এই ছবিটি বিশ্লেষণ করে নিচের বিষয়গুলো যাচাই করা:
    ১. রিভার্স ইমেজ সার্চ এনালাইসিস: এই ছবিটি কি কোনো পুরোনো, বিখ্যাত বা পরিচিত ঘটনার? যদি হয়, তবে আসল ঘটনা, আনুমানিক তারিখ এবং স্থান উল্লেখ করুন। 
    ২. আউট-অফ-কনটেক্সট (Out-of-Context): ছবিটি কি পুরোনো কিন্তু বর্তমানের কোনো ভুয়া দাবিতে ছড়ানো হতে পারে?
    ৩. এডিটিং/এআই জেনারেটেড: ছবিটি কি এআই (Deepfake/Midjourney/DALL-E) দিয়ে তৈরি নাকি ফটোশপে এডিট করা?
    
    আউটপুট অবশ্যই নিচের JSON ফরম্যাটে দিন (অন্য কোনো টেক্সট দেবেন না):
    {
      "verdict": "সত্য (True)" | "মিথ্যা (Fake)" | "বিভ্রান্তিকর (Misleading)" | "অনিশ্চিত (Unverified)",
      "trust_score": 0 থেকে 100 (ছবি রিয়েল এবং সঠিক কনটেক্সটে হলে বেশি, ফেক বা পুরোনো হলে কম),
      "explanation": "১-৩ বাক্যে আসল ঘটনা/তারিখ (যদি জানা থাকে) এবং এডিটিং বা অসংগতির বিস্তারিত।"
    }
    """
    
    if not gemini_key or gemini_key.startswith("your_"):
        return VerdictEnum.UNVERIFIED, 50, "Gemini API Key সেট করা নেই।"

    try:
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": encoded_image
                                }
                            }
                        ]
                    }],
                    "generationConfig": {"response_mime_type": "application/json"}
                }, timeout=30.0
            )
            if res.status_code == 200:
                parsed = json.loads(res.json()["candidates"][0]["content"]["parts"][0]["text"])
                return parse_verdict(parsed.get("verdict", "")), int(parsed.get("trust_score", 0)), parsed.get("explanation", "")
            else:
                print(f"API Error in Image Analysis: {res.text}")
    except Exception as e:
        print(f"Image Analysis Error: {e}")
        
    return VerdictEnum.UNVERIFIED, 50, "ছবি যাচাইয়ের সময় সার্ভারে বা এআই-তে সমস্যা হয়েছে।"