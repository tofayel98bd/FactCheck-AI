import os
import httpx
from typing import List
from models.schemas import SourceItem

# ভেরিফায়েড সোর্সের তালিকা (Whitelisting)
TRUSTED_SOURCES = [
    "prothomalo.com", "bdnews24.com", "thedailystar.net", "ntvbd.com", 
    "somoynews.tv", "jamuna.tv", "independent24.com", "ittefaq.com.bd", 
    "kalerkantho.com", "jugantor.com", "samakal.com", "dhakatribune.com", 
    "tbsnews.net", "channelionline.com", "banglatribune.com", "jagonews24.com", 
    "banglanews24.com", "mzamin.com", "deshrupantor.com", "dailynayadiganta.com", 
    "inqilab.com", "bd-pratidin.com", "amadershomoy.com", "bhorerkagoj.com", 
    "ajkerpatrika.com", "dbcnews.tv", "ekushey-tv.com", "rtvonline.com", 
    "channel24bd.tv", "banglavision.tv", "news24bd.tv", "newagebd.net", 
    "thefinancialexpress.com.bd", "daily-sun.com", "observerbd.com", 
    "bssnews.net", "unb.com.bd",
    "bbc.com", "reuters.com", "apnews.com", "aljazeera.com", "cnn.com", 
    "theguardian.com", "nytimes.com", "washingtonpost.com", "bloomberg.com", 
    "afp.com", "wsj.com", "ft.com", "cnbc.com", "foxnews.com", "nbcnews.com", 
    "cbsnews.com", "abcnews.go.com", "time.com", "economist.com", "npr.org", 
    "pbs.org", "dw.com", "france24.com", "independent.co.uk", "telegraph.co.uk", 
    "thetimes.co.uk", "scmp.com", "japantimes.co.jp", "kyodonews.net", 
    "timesofindia.indiatimes.com", "thehindu.com", "ndtv.com", "dawn.com", 
    "politico.com", "axios.com"
]

async def search_web(query: str, max_results: int = 5) -> List[SourceItem]:
    serper_api_key = os.getenv("SERPER_API_KEY")
    google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    fetch_limit = 20 

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
                    json={
                        "q": query,
                        "num": fetch_limit,
                        "gl": "bd",
                        "hl": "bn"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic", [])
                    sources = []
                    
                    for item in organic_results:
                        link = item.get("link", "").lower()
                        # Strict whitelisting match
                        if any(domain in link for domain in TRUSTED_SOURCES):
                            sources.append(SourceItem(
                                title=item.get("title", "No Title"),
                                url=item.get("link", ""),
                                snippet=item.get("snippet", "")
                            ))
                        if len(sources) >= max_results:
                            break
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
                        "num": fetch_limit if fetch_limit <= 10 else 10
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    sources = []
                    
                    for item in items:
                        link = item.get("link", "").lower()
                        # Strict whitelisting match
                        if any(domain in link for domain in TRUSTED_SOURCES):
                            sources.append(SourceItem(
                                title=item.get("title", "No Title"),
                                url=item.get("link", ""),
                                snippet=item.get("snippet", "")
                            ))
                        if len(sources) >= max_results:
                            break
                    return sources
        except Exception as e:
            print(f"[Search Engine Error] Google search failed: {e}")

    print("[Search Engine Notice] No active Search API Key found.")
    return [
        SourceItem(
            title="প্রথম আলো - শীর্ষ সংবাদ ও তথ্য যাচাই",
            url="https://www.prothomalo.com",
            snippet=f"দাবি সম্পর্কিত তথ্য অনুসন্ধান করা হচ্ছে: '{query[:50]}...'"
        )
    ]