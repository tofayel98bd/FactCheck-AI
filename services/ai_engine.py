import os
import json
import httpx
from typing import List
from models.schemas import VerdictEnum, SourceItem, FactCheckResponse

async def analyze_claim_with_rag(claim: str, sources: List[SourceItem], language: str = "bn") -> tuple[VerdictEnum, int, str]:
    """
    Analyzes the claim against retrieved search sources using LLM (Gemini or OpenAI).
    Applies RAG principles, hallucination guardrails, and trust scoring.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Format search evidence for RAG context
    evidence_text = "\n".join([
        f"- উৎস {idx}: {s.title}\n  ইউআরএল: {s.url}\n  সারাংশ: {s.snippet}"
        for idx, s in enumerate(sources, 1)
    ]) if sources else "কোন তথ্যসূত্র পাওয়া যায়নি।"

    prompt = f"""
আপনি একজন পেশাদার এবং নিরপেক্ষ ফ্যাক্ট-চেকার (Fact-Checker)। নিচের সামাজিক মাধ্যম বা সংবাদের দাবিটি যাচাই করুন।

[যাচাইয়ের দাবি]:
"{claim}"

[অনলাইন অনুসন্ধান থেকে প্রাপ্ত তথ্যপ্রমাণ (RAG Evidence)]:
{evidence_text}

[নির্দেশনা]:
১. প্রাপ্ত তথ্যপ্রমাণের ভিত্তিতে দাবিটির সত্যতা যাচাই করুন।
২. যদি তথ্যপ্রমাণে সরাসরি কোনো মূলধারার বিশ্বস্ত সোর্স বা সরকারি সোর্সের স্বীকৃতি থাকে তবে সত্য/মিথ্যা নির্ধারণ করুন।
৩. যদি পর্যাপ্ত নির্ভরযোগ্য প্রমাণ না থাকে, তবে নিজেকে অনুমান বা বানিয়ে লেখা (Hallucination) থেকে বিরত থাকুন এবং "অনিশ্চিত (Unverified)" লেবেল বেছে নিন।
৪. আউটপুট অবশ্যই নিচের বৈধ JSON ফরম্যাটে দিন:

{{
  "verdict": "সত্য (True)" | "মিথ্যা (Fake)" | "বিভ্রান্তিকর (Misleading)" | "অনিশ্চিত (Unverified)",
  "trust_score": 0 থেকে 100 এর মধ্যে সংখ্যা,
  "explanation": "১-৩ বাক্যে স্পষ্ট ও যুক্তিনির্ভর ব্যাখ্যা"
}}
    """

    # 1. Try Gemini API
    if gemini_key and not gemini_key.startswith("your_"):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    },
                    timeout=15.0
                )
                if res.status_code == 200:
                    result_json = res.json()
                    raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    verdict_str = parsed.get("verdict", VerdictEnum.UNVERIFIED.value)
                    trust_score = int(parsed.get("trust_score", 50))
                    explanation = parsed.get("explanation", "তথ্যটি যাচাই করা হয়েছে।")
                    return parse_verdict(verdict_str), trust_score, explanation
        except Exception as e:
            print(f"[AI Engine Error] Gemini API failed: {e}")

    # 2. Try OpenAI API
    if openai_key and not openai_key.startswith("your_"):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=15.0
                )
                if res.status_code == 200:
                    raw_text = res.json()["choices"][0]["message"]["content"]
                    parsed = json.loads(raw_text)
                    verdict_str = parsed.get("verdict", VerdictEnum.UNVERIFIED.value)
                    trust_score = int(parsed.get("trust_score", 50))
                    explanation = parsed.get("explanation", "তথ্যটি যাচাই করা হয়েছে।")
                    return parse_verdict(verdict_str), trust_score, explanation
        except Exception as e:
            print(f"[AI Engine Error] OpenAI API failed: {e}")

    # Fallback response if no LLM API Key is configured
    return (
        VerdictEnum.UNVERIFIED,
        50,
        "কোনো সক্রিয় AI API Key (Gemini/OpenAI) পাওয়া যায়নি। এটি টেস্ট মোড রেজাল্ট। আসল রেসপন্স পেতে `.env` ফাইলে API Key যুক্ত করুন।"
    )

def parse_verdict(val: str) -> VerdictEnum:
    if "সত্য" in val or "True" in val:
        return VerdictEnum.TRUE
    elif "মিথ্যা" in val or "Fake" in val:
        return VerdictEnum.FAKE
    elif "বিভ্রান্তিকর" in val or "Misleading" in val:
        return VerdictEnum.MISLEADING
    else:
        return VerdictEnum.UNVERIFIED
