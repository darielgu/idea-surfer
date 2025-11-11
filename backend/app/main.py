import logging
import os
import traceback

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from app.routes.scraper_routes import router as scraper_router
from app.routes.search import router as search

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

logger = logging.getLogger("uvicorn.error")

app = FastAPI(debug=True)

redis_conn: redis.Redis | None = None


@app.on_event("startup")
async def startup():
    global redis_conn
    try:
        if not REDIS_URL:
            logger.warning("REDIS_URL is not set; rate limiting is DISABLED")
            return

        logger.info(f"Connecting to Redis at {REDIS_URL!r}")
        redis_conn = await redis.from_url(
            REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_conn)
        logger.info("FastAPILimiter initialized")
    except Exception as e:
        logger.error(
            "Error during startup:\n%s",
            "".join(traceback.format_exception(type(e), e, e.__traceback__)),
        )
        # Optionally re-raise if you want deployment to fail
        # raise


@app.on_event("shutdown")
async def shutdown():
    global redis_conn
    if redis_conn is not None:
        await redis_conn.close()
        logger.info("Redis connection closed")


# Global exception logger so you see real errors in Vercel logs
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception for %s %s:\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


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

app.include_router(scraper_router)
app.include_router(search)


@app.get("/")
async def read_root():
    return {"message": "Welcome to IdeaSurf API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
