from app.services.db.supa_base_client import supa_base_client
from app.services.embedder.embedder import embded_query
from fastapi import APIRouter, Query

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def search(search_query: str = Query(..., description="User search query")):
    """Endpoint to perform a search based on the query string."""
    embedding = embded_query(search_query)
    response = supa_base_client.rpc(
        "match_projects",  # custom RPC we'll define below
        {"query_embedding": embedding},
    ).execute()

    results = response.data if response.data else []

    return {"query": search_query, "results": results}
