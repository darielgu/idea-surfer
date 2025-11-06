import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from app.routes.scraper_routes import router as scraper_router

app = FastAPI()
app.include_router(scraper_router)


class SearchQuery(BaseModel):
    prompt: str


@app.get("/")
async def read_root():
    return {"message": "Welcome to IdeaSurf API"}


@app.get("/search/")
async def search(search_query: SearchQuery):
    # return dummy results and echo the query
    return {"query": search_query.prompt, "results": ["idea1", "idea2", "idea3"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
