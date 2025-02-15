from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.visitors import Visitor
from src.db import get_db
import httpx
import ipaddress

visitor_router = APIRouter()


async def get_public_ip():
    """Fetches the public IPv4 address asynchronously using Cloudflare."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://1.1.1.1/cdn-cgi/trace")
            response.raise_for_status()
            data = response.text.split("\n")
            for line in data:
                if line.startswith("ip="):
                    return line.split("=")[1].strip()
    except httpx.RequestError as e:
        print(f"Error fetching public IP: {e}")
        return None


def is_private_ip(ip: str) -> bool:
    """Checks if an IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True  # Invalid IPs are considered private


@visitor_router.post("/log-visitor")
async def log_visitor(request: Request, db: Session = Depends(get_db)):
    """
    Log visitor details (Public IPv4 address and User-Agent) into the database.
    """
    try:
        forwarded_ips = request.headers.get("x-forwarded-for")
        public_ip = None

        if forwarded_ips:
            ip_list = [ip.strip() for ip in forwarded_ips.split(",")]
            for ip in ip_list:
                if not is_private_ip(ip):
                    public_ip = ip
                    break

        if not public_ip:
            public_ip = await get_public_ip()

        if not public_ip:
            public_ip = request.client.host

        if not public_ip or is_private_ip(public_ip):
            raise HTTPException(status_code=500, detail="Failed to retrieve public IP")

        user_agent = request.headers.get("user-agent")

        existing_visitor = db.query(Visitor).filter(
            Visitor.ip_address == public_ip,
            Visitor.user_agent == user_agent
        ).first()

        if existing_visitor:
            return {"message": "Visitor already logged", "ip": public_ip}

        visitor = Visitor(ip_address=public_ip, user_agent=user_agent)
        db.add(visitor)
        db.commit()

        return {"message": "Visitor logged", "ip": public_ip}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while logging the visitor.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@visitor_router.get("/visitor-count")
def get_visitor_count(db: Session = Depends(get_db)):
    """
    Retrieve the total number of visitors from the database.
    """
    try:
        count = db.query(Visitor).count()
        return {"count": count}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving the visitor count.")



@visitor_router.get("/get-visitor-details")
def get_visitor_details(db: Session = Depends(get_db)):
    """
    Retrieve the visitor details from the database.
    """
    try:
        visitors = db.query(Visitor).all()
        return visitors
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving the visitor details.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    


