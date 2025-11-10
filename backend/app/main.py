import os

import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from app.routes.scraper_routes import router as scraper_router
from app.routes.search import router as search

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    yield
    await r.close()  # type: ignore


app = FastAPI(lifespan=lifespan)  # type: ignore
app.include_router(scraper_router)
app.include_router(search)
origins = [
    "http://localhost:3000",
    "https://idea-surfer-fe.vercel.app",
    "http://idea-surfer-fe.vercel.app",
    "https://ideasurfer.xyz",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to IdeaSurf API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
