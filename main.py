from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import feedparser
import os

app = FastAPI(
    title="AI Job Backend",
    description="Fetches and analyzes job listings from Indeed RSS feeds.",
    version="1.0.0"
)

# Allow requests from any frontend (React, Vercel, Netlify, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root endpoint for Render health check
@app.get("/")
def home():
    return {"message": "✅ AI Job Backend is running successfully!"}


# ✅ Job search endpoint
@app.get("/search")
def search_jobs(keyword: str = Query(..., min_length=2, description="Job keyword to search")):
    """
    Fetch top 10 job listings from Indeed RSS feed based on keyword.
    """
    try:
        feed_url = f"https://rss.indeed.com/rss?q={keyword.replace(' ', '+')}"
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            return {"message": f"No jobs found for '{keyword}'"}

        jobs = []
        for entry in feed.entries[:10]:
            jobs.append({
                "title": entry.title,
                "company": getattr(entry, "author", "Unknown"),
                "link": entry.link,
                "description": getattr(entry, "summary", ""),
                "match_score": 0
            })

        return {"keyword": keyword, "count": len(jobs), "results": jobs}

    except Exception as e:
        return {"error": str(e)}
