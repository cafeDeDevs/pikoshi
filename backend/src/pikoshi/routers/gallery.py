from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..services.s3_service import S3Service

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


@router.post("/default/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    # Create a unique id per user and store it in the DB as s3_bucket_id
    # grab the user's PK id from the redis cache utilizing the access_token:
    # NOTE: UUIDs can be randomly generated using python's native uuid4 package
    # NOTE: Consider hashing the UUID (or using a different variation of uuid)
    # NOTE: Do NOT generate the UUID here obviously...

    # user_id = int(await redis.get(f"auth_session_{access_token}"))
    # Use the PK id to grab the user's s3_bucket_id

    # Create a bucket named by that s3_bucket_id (errors to logger if bucket already exists)
    # NOTE: Create the bucket's name based off the first character of the UUID only

    # Instantiate a variable named bucket_name that stores the string of the newly created bucket
    # S3Service.grab_file_list(bucket_name) by that bucket_name and store it in a variable called file_list
    # Instantiate a new emtpy List called image_files
    # If the file_list is empty, upload a default.jpg file to the bucket in a newly created directory called "default"
    # Iterate over the file_list List, and if the string "default/" exists in the file name:
    # If the string "default/" DOES EXIST, THEN:
    #  file_obj = s3_client.get_object(Bucket=bucket_name, Key=file)
    #  image_data = base64.b64encode(file_obj["Body"].read()).decode("utf-8")
    #  image_files.append(image_data)
    # Return a 200 OK HTTP Response Object (not JSON??) that has the image_files list in a field titled "images_as_base_64"
    # Handle Exceptions
    return JSONResponse(status_code=200, content={"message": "Hello World!"})


#  @router.post("/upload/")
#  async def upload_image_to_gallery(
#  access_token: Annotated[str | None, Cookie()] = None,
#  refresh_token: Annotated[str | None, Cookie()] = None,
#  db: Session = Depends(get_db),
#  ) -> Response:
