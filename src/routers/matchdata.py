from fastapi import APIRouter, HTTPException
import httpx
from src.schemas.matchdata import UrlRequest

match_router = APIRouter()


@match_router.post("/fetch-data", summary="Fetch data from the given URL")
async def fetch_data(url_request: UrlRequest):
    """
    Asynchronously fetch data from the provided URL.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_request.url)
            response.raise_for_status()  
            return response.json()  
    except httpx.HTTPStatusError as http_exc:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP error occurred: {response.text}"
        ) from http_exc
    except httpx.RequestError as req_exc:
        raise HTTPException(
            status_code=500,
            detail=f"Request error occurred: {str(req_exc)}"
        ) from req_exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(exc)}"
        ) from exc
