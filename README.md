# FactCheck AI (ফ্যাক্টচেক এআই) 🤖🇧🇩

> **তাৎক্ষণিক এআই-চালিত তথ্য ও গুজব যাচাইকারী প্ল্যাটফর্ম — ব্যাকএন্ড এপিআই সার্ভিস (Phase 2)**

FactCheck AI হলো একটি রিয়েল-টাইম এআই সিস্টেম, যা ইন্টারনেটে ছড়িয়ে পড়া খবর, সোশাল মিডিয়া পোস্ট বা গুজবের সত্যতা ১-২ মিনিটের মধ্যে যাচাই করে প্রমাণের লিংক ও ট্রাস্ট স্কোরসহ নিরপেক্ষ রিপোর্ট প্রদান করে।

---

## 🚀 ফেজ ২ (Phase 2) - যা সম্পন্ন হয়েছে

- **FastAPI Async Engine:** উচ্চগতির কনকারেন্ট রিকোয়েস্ট হ্যান্ডলিং ও ব্যাকএন্ড আর্কিটেকচার।
- **Real-Time Web Search Service:** Serper.dev API এবং Google Custom Search API ইন্টিগ্রেশন।
- **AI RAG & Hallucination Guardrails:** Google Gemini API (Grounding) এবং OpenAI GPT-4o ব্যবহার করে প্রম্পট-ইঞ্জিনিয়ারিং ও মনগড়া তথ্য (Hallucination) প্রতিরোধ।
- **Trust Scoring Engine:** সংগৃহীত খবরের সোর্স বিশ্বাসযোগ্যতা বিশ্লেষণ করে ০-১০০% ট্রাস্ট স্কোর এবং প্রমাণের সোর্স লিংক প্রদান।

---

## 📂 প্রজেক্ট ফোল্ডার স্ট্রাকচার (Folder Structure)

```text
FactCheck-AI/
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic Request & Response Data Models
├── services/
│   ├── __init__.py
│   ├── search.py          # Serper & Google Real-Time Web Search Service
│   └── ai_engine.py       # Gemini/OpenAI RAG & Fact Checking Engine
├── .env.example           # Environment variables configuration template
├── .env                   # Your local secrets & API keys (Git-ignored)
├── main.py                # FastAPI Server Entrypoint
├── requirements.txt       # Project dependencies
├── proposal.txt           # Project Proposal Document
├── guideline.txt          # Project Roadmap & Guidelines
└── README.md              # Project Documentation
```

---

## 🛠️ টিমের জন্য সেটআপ ও রান করার গাইড (Quickstart)

### ১. ডিপেনডেন্সি ইনস্টল করুন
প্রজেক্ট ফোল্ডারে টার্মিনাল খুলে নিচের কমান্ডটি চালান:

```bash
python -m pip install -r requirements.txt --prefer-binary
```

### ২. এনভায়রনমেন্ট ফাইল সেটআপ করুন (`.env`)
`.env.example` ফাইলটিকে কপি করে একটি নতুন `.env` ফাইল তৈরি করুন এবং আপনার API Keys সেট করুন:

```env
PORT=8000
HOST=0.0.0.0

# AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Search API Keys
SERPER_API_KEY=your_serper_api_key_here
```

> 💡 **নোট:** API Key না থাকলেও প্রজেক্টটি **ডেভেলপমেন্ট টেস্ট মোডে** সফলভাবে রান করবে।

### ৩. ব্যাকএন্ড সার্ভার রান করুন
সার্ভার চালু করতে টার্মিনালে লিখুন:

```bash
python -m uvicorn main:app --reload
```
অথবা:
```bash
python main.py
```

সার্ভার সফলভাবে চালু হলে টার্মিনালে দেখাবে:
`INFO: Uvicorn running on http://127.0.0.1:8000`

---

## 🧪 এপিআই ডকুমেন্টেশন ও টেস্টিং (API Documentation)

সার্ভার চালু থাকা অবস্থায় ব্রাউজারে নিচের লিংকে যান:
👉 **`http://localhost:8000/docs`** (Interactive Swagger UI)

### 📌 প্রধান এন্ডপয়েন্ট: `POST /api/verify-fact`

#### Request Payload (JSON):
```json
{
  "claim": "বাংলাদেশে আগামী রবিবার থেকে ১০ দিনের সরকারি ছুটি ঘোষণা করা হয়েছে।",
  "language": "bn"
}
```

#### Response Payload (JSON):
```json
{
  "claim": "বাংলাদেশে আগামী রবিবার থেকে ১০ দিনের সরকারি ছুটি ঘোষণা করা হয়েছে।",
  "verdict": "মিথ্যা (Fake)",
  "trust_score": 95,
  "explanation": "সরকারি গেজেট বা মূলধারার কোনো গণমাধ্যমে ১০ দিনের ছুটির কোনো ঘোষণা পাওয়া যায়নি। এটি একটি অনলাইন গুজব।",
  "sources": [
    {
      "title": "প্রথম আলো - শীর্ষ সংবাদ",
      "url": "https://www.prothomalo.com",
      "snippet": "ভুয়া খবরের সত্যতা যাচাই রিপোর্ট..."
    }
  ],
  "timestamp": "2026-09-11 15:30:00"
}
```

---

## 🤝 অবদান ও পরবর্তী ফেজ (Upcoming Phases)

- **Phase 3:** Telegram Bot API Integration (MVP Bot Setup)
- **Phase 4:** Next.js Web Dashboard & Live Rumor Radar
- **Phase 5:** Cloud Deployment (Render/Vercel)
