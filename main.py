from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="AI Job Backend",
    description="Fetches and analyzes job listings from Remotive Jobs API.",
    version="2.0.0"
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


# ✅ Job search endpoint using Remotive API
@app.get("/search")
def search_jobs(keyword: str = Query(..., min_length=2, description="Job keyword to search")):
    """
    Fetch top 10 job listings from Remotive API based on keyword.
    """
    try:
        api_url = f"https://remotive.com/api/remote-jobs?search={keyword}"
        response = requests.get(api_url)
        data = response.json()

        # If no jobs found
        if not data.get("jobs"):
            return {"message": f"No jobs found for '{keyword}'"}

        jobs = []
        for job in data["jobs"][:10]:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "type": job.get("job_type"),
                "category": job.get("category"),
                "link": job.get("url"),
                "description": job.get("description", "")[:300]  # short preview
            })

        return {
            "keyword": keyword,
            "count": len(jobs),
            "results": jobs
        }

    except Exception as e:
        return {"error": str(e)}
