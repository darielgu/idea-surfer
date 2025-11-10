from app.services.db.supa_base_client import supa_base_client
from app.services.embedder.embedder import embded_query
from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search(query: str = Query(..., description="User search query")):
    """Endpoint to perform a search based on the query string."""
    embedding = embded_query(query)
    response = supa_base_client.rpc(
        "match_projects",  # custom RPC we'll define below
        {"query_embedding": embedding},
    ).execute()

    results = response.data if response.data else []

    return {"query": query, "results": results}
