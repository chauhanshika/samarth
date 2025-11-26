from fastapi import APIRouter
import subprocess
import json
import os

router = APIRouter()

SCRAPER_PATH = "Scraper/main.py"
JOBS_JSON_PATH = "Scraper/jobs.json"


@router.post("/admin/run-scraper")
def run_scraper():
    """
    Runs the external scraper and returns scraped internships
    """

    try:
        result = subprocess.run(
            ["python", SCRAPER_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}

    if not os.path.exists(JOBS_JSON_PATH):
        return {"status": "error", "message": "jobs.json not found"}

    with open(JOBS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "status": "success",
        "scraped_count": len(data),
        "internships": data
    }
