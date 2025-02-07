from fastapi import APIRouter, HTTPException
import httpx

fantasy_router = APIRouter()

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.winbuzz.world',
    'Referer': 'https://www.winbuzz.world/',
}

BASE_URL = "https://zplay1.in/sports/api/v1"

GET_SPORTS_URL = f"{BASE_URL}/sports/management/getSport"
MATCH_URL = f"{BASE_URL}/events/matches"
MATCH_DETAILS_URL = f"{BASE_URL}/events/matchDetails"




async def fetch_json(url: str):
    """Fetch JSON data from a given URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@fantasy_router.get("/getsports", summary="Get Available Sports and IDs")
async def get_sports():
    """Fetch available sports and their IDs."""
    return await fetch_json(GET_SPORTS_URL)

@fantasy_router.get("/inplay", summary="Get In-Play Matches")
async def get_inplay():
    """Fetch ongoing matches."""
    return await fetch_json(f"{MATCH_URL}/inplay")

@fantasy_router.get("/event/{sport_id}", summary="Get Sports Event Data by Sport ID")
async def get_event(sport_id: int):
    """Fetch sports event data using direct sport ID."""
    return await fetch_json(f"{MATCH_URL}/{sport_id}")

@fantasy_router.get("/sport/{match_id}", summary="Get Sports Event Data by Sport ID")
async def get_event(match_id: int):
    """Fetch sports event data using direct sport ID."""
    return await fetch_json(f"{MATCH_DETAILS_URL}/{match_id}")
