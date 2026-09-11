import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.schemas import FactCheckRequest, FactCheckResponse
from services.search import search_web
from services.ai_engine import analyze_claim_with_rag

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="FactCheck AI API Engine",
    description="Real-Time AI-Powered Fact-Checking & Rumor Verification System",
    version="1.0.0"
)

# Enable CORS for frontend & bot integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "Online",
        "system": "FactCheck AI Backend Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "FactCheck AI API is running smoothly."}

@app.post("/api/verify-fact", response_model=FactCheckResponse, tags=["Fact Check"])
async def verify_fact(request: FactCheckRequest):
    """
    Main Fact-Checking Endpoint (Phase 2):
    1. Extracts user claim.
    2. Performs real-time web search (Serper / Google Custom Search).
    3. Runs RAG analysis using LLM (Gemini / OpenAI) with Hallucination Guardrails.
    4. Computes trust score & returns structured report with clickable source links.
    """
    if not request.claim or len(request.claim.strip()) < 5:
        raise HTTPException(status_code=400, detail="দাবিটি অতি সংক্ষিপ্ত বা ফাঁকা। অনুগ্রহ করে স্পষ্ট টেক্সট প্রদান করুন।")

    claim_text = request.claim.strip()

    # Step 1: Real-Time Search & Web Scraping
    sources = await search_web(query=claim_text, max_results=5)

    # Step 2: AI RAG & Trust Scoring Engine
    verdict, trust_score, explanation = await analyze_claim_with_rag(
        claim=claim_text,
        sources=sources,
        language=request.language
    )

    # Step 3: Construct Response
    return FactCheckResponse(
        claim=claim_text,
        verdict=verdict,
        trust_score=trust_score,
        explanation=explanation,
        sources=sources,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
