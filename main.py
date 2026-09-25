import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.schemas import FactCheckRequest, FactCheckResponse
from services.search import search_web
from services.ai_engine import analyze_claim_with_rag, analyze_image_with_ai

load_dotenv()

app = FastAPI(
    title="FactCheck AI API Engine",
    description="Real-Time AI-Powered Fact-Checking & Rumor Verification System",
    version="1.0.0"
)

# 🔹 CORS ফিক্স করা হয়েছে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # এটি False করা হয়েছে
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

@app.post("/api/verify-fact", response_model=FactCheckResponse, tags=["Fact Check"])
async def verify_fact(request: FactCheckRequest):
    if not request.claim or len(request.claim.strip()) < 5:
        raise HTTPException(status_code=400, detail="দাবিটি অতি সংক্ষিপ্ত বা ফাঁকা।")

    claim_text = request.claim.strip()
    sources = await search_web(query=claim_text, max_results=5)
    
    verdict, trust_score, explanation = await analyze_claim_with_rag(
        claim=claim_text,
        sources=sources,
        language=request.language
    )

    return FactCheckResponse(
        claim=claim_text,
        verdict=verdict,
        trust_score=trust_score,
        explanation=explanation,
        sources=sources,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/api/verify-image", response_model=FactCheckResponse, tags=["Fact Check - Image"])
async def verify_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    verdict, trust_score, explanation = await analyze_image_with_ai(image_bytes)
    
    return FactCheckResponse(
        claim="[ছবি বিশ্লেষণ]",
        verdict=verdict,
        trust_score=trust_score,
        explanation=explanation,
        sources=[],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)