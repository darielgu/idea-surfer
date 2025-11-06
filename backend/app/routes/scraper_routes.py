from app.services.scraper.yc import run_scrape_yc
from fastapi import APIRouter

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/yc/")
async def scrape_yc_batches(batches: list[str]):
    """Endpoint to trigger YC scraper for specified batches. FOR USER - Enter BATCH as LIST OF STRINGS EX ["Fall 2023"]"""
    run_scrape_yc(batches)
    return {"message": f"Scraping initiated for batches: {batches}"}
