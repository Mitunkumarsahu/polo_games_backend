import uvicorn
from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.bannerimage import image_router
from src.routers.otp import otp_router
from src.routers.blog import blog_router
from src.routers.reel import reel_router
from src.db import initialize_database
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
app.include_router(image_router, prefix="/admin", tags=["Images"])
app.include_router(otp_router, prefix="/otp", tags=["OTP"])
app.include_router(blog_router, prefix="/blogs", tags=["Blogs"])
app.include_router(reel_router, prefix="/reels", tags=["Reels"])

@app.on_event("startup")
def startup_event():
    """
    Event triggered on application startup to initialize the database.
    """
    initialize_database()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
