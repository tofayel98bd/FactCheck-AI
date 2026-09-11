from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class VerdictEnum(str, Enum):
    TRUE = "সত্য (True)"
    FAKE = "মিথ্যা (Fake)"
    MISLEADING = "বিভ্রান্তিকর (Misleading)"
    UNVERIFIED = "অনিশ্চিত (Unverified)"

class FactCheckRequest(BaseModel):
    claim: str = Field(..., description="The news claim, social media post text, or rumor to verify", example="বাংলাদেশে আগামী রবিবার থেকে ১০ দিনের সরকারি ছুটি ঘোষণা করা হয়েছে।")
    language: Optional[str] = Field("bn", description="Language of response ('bn' for Bangla, 'en' for English)")

class SourceItem(BaseModel):
    title: str = Field(..., description="Title of the news article or source")
    url: str = Field(..., description="Clickable reference URL")
    snippet: Optional[str] = Field(None, description="Excerpt or snippet from the article")

class FactCheckResponse(BaseModel):
    claim: str
    verdict: VerdictEnum
    trust_score: int = Field(..., ge=0, le=100, description="Credibility percentage score (0-100%)")
    explanation: str = Field(..., description="Logical reasoning and context provided by AI")
    sources: List[SourceItem] = Field(default_factory=list, description="Top evidence links retrieved from real-time web search")
    timestamp: str
