from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

reel_router = APIRouter()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, BUCKET_NAME]):
    raise RuntimeError("AWS configuration is incomplete. Please check environment variables.")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


@reel_router.post("/upload-reel/")
async def upload_reel(file: UploadFile = File(...)):
    """
    Upload a video file to the S3 bucket.
    
    Args:
        file (UploadFile): The video file to be uploaded.
    
    Returns:
        JSONResponse: A message and the URL of the uploaded file.
    """
    try:
        if file.content_type not in ["video/mp4", "video/mov", "video/avi"]:
            raise HTTPException(
                status_code=400, detail="Invalid file type. Only MP4, MOV, and AVI are allowed."
            )

        file_key = f"reels/{file.filename}"
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file_key)
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"

        return JSONResponse(
            content={"message": "File uploaded successfully", "url": file_url}, status_code=200
        )
    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS error occurred: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@reel_router.get("/get-reels/")
async def get_reels():
    """
    Fetch the list of all reel URLs from the S3 bucket.
    
    Returns:
        List[str]: A list of reel URLs.
    """
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="reels/")
        if "Contents" not in response:
            return JSONResponse(content={"message": "No reels found"}, status_code=200)

        reel_urls = [
            f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{item['Key']}"
            for item in response["Contents"]
        ]
        return reel_urls
    except ClientError as e:
        raise HTTPException(status_code=500, detail="AWS client error occurred: " + str(e))
    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS error occurred: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@reel_router.delete("/delete-reel/{filename}")
async def delete_reel(filename: str):
    """
    Delete a specific reel from the S3 bucket.

    Args:
        filename (str): The name of the file to be deleted.

    Returns:
        JSONResponse: A message indicating the success or failure of the operation.
    """
    try:
        file_key = f"reels/{filename}"
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)

        return JSONResponse(
            content={"message": f"Reel '{filename}' deleted successfully"}, status_code=200
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail=f"Reel '{filename}' not found in the bucket")
    except ClientError as e:
        raise HTTPException(status_code=500, detail="AWS client error occurred: " + str(e))
    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS error occurred: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
