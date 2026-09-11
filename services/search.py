import os
import httpx
from typing import List
from models.schemas import SourceItem

async def search_web(query: str, max_results: int = 5) -> List[SourceItem]:
    """
    Performs real-time web search using Serper API or Google Custom Search API.
    Falls back to mock results if no API key is set.
    """
    serper_api_key = os.getenv("SERPER_API_KEY")
    google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    # 1. Serper API
    if serper_api_key and not serper_api_key.startswith("your_"):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={"q": query, "num": max_results, "gl": "bd", "hl": "bn"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic", [])
                    sources = []
                    for item in organic_results[:max_results]:
                        sources.append(SourceItem(
                            title=item.get("title", "No Title"),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", "")
                        ))
                    return sources
        except Exception as e:
            print(f"[Search Engine Error] Serper search failed: {e}")

    # 2. Google Custom Search API
    if google_api_key and google_cx:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": google_api_key,
                        "cx": google_cx,
                        "q": query,
                        "num": max_results
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    sources = []
                    for item in items[:max_results]:
                        sources.append(SourceItem(
                            title=item.get("title", "No Title"),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", "")
                        ))
                    return sources
        except Exception as e:
            print(f"[Search Engine Error] Google search failed: {e}")

    # Fallback/Mock Search Mode if no search API key is configured
    print("[Search Engine Notice] No active Search API Key found. Returning placeholder search results for development.")
    return [
        SourceItem(
            title="প্রথম আলো - শীর্ষ সংবাদ ও তথ্য যাচাই",
            url="https://www.prothomalo.com",
            snippet=f"দাবি সম্পর্কিত তথ্য অনুসন্ধান করা হচ্ছে: '{query[:50]}...'"
        ),
        SourceItem(
            title="রুমোর স্ক্যানার বাংলাদেশ - ফ্যাক্ট চেক",
            url="https://rumorscanner.com/bangladesh",
            snippet=f"অনলাইন গুজব ও তথ্যের যাচাইকরণ রিপোর্ট: '{query[:50]}...'"
        )
    ]
