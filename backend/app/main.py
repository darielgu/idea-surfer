import uvicorn
from fastapi import FastAPI

from app.routes.scraper_routes import router as scraper_router
from app.routes.search import router as search

app = FastAPI()
app.include_router(scraper_router)
app.include_router(search)


@app.get("/")
async def read_root():
    return {"message": "Welcome to IdeaSurf API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
