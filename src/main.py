import uvicorn
from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.bannerimage import image_router
from src.routers.otp import otp_router


app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["Users"])
app.include_router(image_router, prefix="/admin", tags=["Images"])
app.include_router(otp_router, prefix="/otp", tags=["OTP"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)