from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
import os

app = FastAPI()

# Allow requests from anywhere (for your React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_jobs(keyword: str):
    """Fetch job results from Indeed RSS feed."""
    feed_url = f"https://rss.indeed.com/rss?q={keyword.replace(' ', '+')}"
    feed = feedparser.parse(feed_url)
    jobs = []

    for entry in feed.entries[:10]:
        jobs.append({
            "title": entry.title,
            "company": getattr(entry, "author", "Unknown"),
            "link": entry.link,
            "description": getattr(entry, "summary", ""),
            "match_score": 0
        })

    return jobs
