from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="AI Job Backend",
    description="Fetches and analyzes job listings from Remotive API.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "✅ AI Job Backend is running successfully!"}

@app.get("/search")
def search_jobs(
    keyword: str = Query(..., min_length=2, description="Job keyword to search"),
    location: str = Query("", description="Candidate location or remote flag"),
    job_type: str = Query("", description="Job type like full_time, contract, internship"),
    limit: int = Query(10, gt=0, le=50, description="Number of results to return (max 50)")
):
    try:
        api_url = f"https://remotive.com/api/remote-jobs?search={keyword}"
        if job_type:
            api_url += f"&job_type={job_type}"
        # Remotive does not provide direct ‘location’ param; we filter later
        api_url += f"&limit={limit}"

        response = requests.get(api_url)
        data = response.json()
        jobs_raw = data.get("jobs", [])

        # Filter by location if provided
        if location:
            loc_lower = location.lower()
            jobs_filtered = [
                job for job in jobs_raw
                if loc_lower in (job.get("candidate_required_location") or "").lower()
                   or ("remote" in job.get("candidate_required_location","").lower())
            ]
        else:
            jobs_filtered = jobs_raw

        results = jobs_filtered[:limit]
        if not results:
            return {"message": f"No jobs found for '{keyword}' with filters"}

        jobs = []
        for job in results:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "type": job.get("job_type"),
                "category": job.get("category"),
                "link": job.get("url"),
                "salary": job.get("salary"),
                "description": job.get("description","")[:300]
            })

        return {"keyword": keyword, "count": len(jobs), "results": jobs}

    except Exception as e:
        return {"error": str(e)}
