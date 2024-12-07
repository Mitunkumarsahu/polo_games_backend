import uvicorn
from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.bannerimage import image_router
from src.routers.otp import otp_router
from src.routers.blog import blog_router
from src.db import initialize_database

app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["Users"])
app.include_router(image_router, prefix="/admin", tags=["Images"])
app.include_router(otp_router, prefix="/otp", tags=["OTP"])
app.include_router(blog_router, prefix="/blogs", tags=["Blogs"])

@app.on_event("startup")
def startup_event():
    """
    Event triggered on application startup to initialize the database.
    """
    initialize_database()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
