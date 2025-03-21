import uvicorn
from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.superadmin import superadmin_router
from src.routers.bannerimage import image_router
from src.routers.bannerimagemobile import banner_image_router_for_mobile
from src.routers.otp import otp_router
from src.routers.blog import blog_router
from src.routers.reel import reel_router
from src.routers.marqueetext import marqueetext_router
from src.routers.imagelinkrouter import image_link_router
from src.routers.imagelinkrouterforbackup import image_link_router_for_backup
from src.routers.visitors import visitor_router
from src.routers.offer import offer_router
from src.routers.socialmedia import socialmedia_router
from src.routers.worldbook import world_book_router
from src.db import initialize_database
from src.firstsuperadmin import create_first_superadmin
from fastapi.middleware.cors import CORSMiddleware

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuth2 as OAuth2Model
from fastapi.openapi.utils import get_openapi

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API with OAuth2 Bearer Token",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/user", tags=["Users"])
app.include_router(superadmin_router, prefix="/api/superadmin", tags=["SuperAdmins"])
app.include_router(image_router, prefix="/api/bannerimage", tags=["Images"])
app.include_router(banner_image_router_for_mobile, prefix="/api/bannerimagemobile", tags=["Images Mobile"])
app.include_router(otp_router, prefix="/api/otp", tags=["OTP"])
app.include_router(blog_router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(reel_router, prefix="/api/reels", tags=["Reels"])
app.include_router(marqueetext_router, prefix="/api/marqueetext", tags=["MarqueeText"])
app.include_router(image_link_router, prefix="/api/imagelink", tags=["ImageLink"])
app.include_router(image_link_router_for_backup, prefix="/api/imagelinkforbackup", tags=["ImageLinkForBackup"])
app.include_router(world_book_router, prefix="/api/worldbook", tags=["WorldBook"])
app.include_router(visitor_router, prefix="/api/visitors", tags=["Visitors"])
app.include_router(offer_router, prefix="/api/offers", tags=["Offers"])
app.include_router(socialmedia_router, prefix="/api/socialmedia", tags=["SocialMedia"])

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
