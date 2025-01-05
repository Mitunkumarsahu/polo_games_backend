import uvicorn
from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.admin import admin_router
from src.routers.superadmin import superadmin_router
from src.routers.bannerimage import image_router
from src.routers.otp import otp_router
from src.routers.blog import blog_router
from src.routers.reel import reel_router
from src.routers.marqueetext import marqueetext_router
from src.routers.imagelinkrouter import image_link_router
from src.routers.visitors import visitor_router
from src.routers.offer import offer_router
from src.db import initialize_database
from src.firstsuperadmin import create_first_superadmin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/user", tags=["Users"])
app.include_router(admin_router, prefix="/admin", tags=["Admins"])
app.include_router(superadmin_router, prefix="/superadmin", tags=["SuperAdmins"])
app.include_router(image_router, prefix="/admin", tags=["Images"])
app.include_router(otp_router, prefix="/otp", tags=["OTP"])
app.include_router(blog_router, prefix="/blogs", tags=["Blogs"])
app.include_router(reel_router, prefix="/reels", tags=["Reels"])
app.include_router(marqueetext_router, prefix="/marqueetext", tags=["MarqueeText"])
app.include_router(image_link_router, prefix="/imagelink", tags=["ImageLink"])
app.include_router(visitor_router, prefix="/visitors", tags=["Visitors"])
app.include_router(offer_router, prefix="/offers", tags=["Offers"])

@app.on_event("startup")
def startup_event():
    """
    Event triggered on application startup to initialize the database 
    and create the first superadmin if the database initialization succeeds.
    """
    if initialize_database():
        create_first_superadmin()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
