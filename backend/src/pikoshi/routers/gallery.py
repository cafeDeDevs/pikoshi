from base64 import b64encode
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..services.exception_handler_service import ExceptionService
from ..services.s3_service import S3Service
from ..services.user_service import get_user

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


# TODO: Figure out how to get parameters which will lead to the album name
# NOTE: IF parameter album_name == None, then default it to "default"
@router.post("/default/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    # TODO: Refactor this into more service file/helper functions in s3_service.py
    try:
        user_id = int(await redis.get(f"auth_session_{access_token}"))

        s3_client = S3Service.get_s3_client()

        user = get_user(db, user_id)
        user_uuid = str(user.uuid)

        user_bucket_index = S3Service.get_bucket_index(user_uuid)  # type:ignore
        bucket_name = f"user-bucket-{user_bucket_index}"
        S3Service.create_bucket(bucket_name, user_uuid, album_name="default")

        file_list = S3Service.grab_file_list(bucket_name, user_uuid)

        if len(file_list) == 0:
            S3Service.upload_file(
                file_name="./src/pikoshi/public/default.jpg",
                bucket_name=bucket_name,
                user_uuid=user_uuid,
                object_name="default.jpg",
                album_name="default",
            )

        file_list = S3Service.grab_file_list(
            bucket_name, user_uuid, album_name="default"
        )
        image_files = []

        # TODO: Once album_name is grabbed from parameters, change this
        for file_name in file_list:
            if "/default/" in file_name:
                file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_name)
                image_data = b64encode(file_obj["Body"].read()).decode("utf-8")
                image_files.append(image_data)

        if len(image_files) == 0:
            raise HTTPException(
                status_code=400, detail="No Images Found In Default Album."
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Images Retrieved From S3 And Sent To Client Successfully.",
                "imagesAsBase64": image_files,
            },
        )
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except Exception as e:
        return ExceptionService.handle_s3_exception(e)


#  @router.post("/upload/")
#  async def upload_image_to_gallery(
#  access_token: Annotated[str | None, Cookie()] = None,
#  refresh_token: Annotated[str | None, Cookie()] = None,
#  db: Session = Depends(get_db),
#  ) -> Response:
