from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..services.exception_handler_service import ExceptionService
from ..services.gallery_service import GalleryService

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


# TODO: Figure out how to get parameters which will lead to the album name
# NOTE: IF parameter album_name == None, then default it to "default"
@router.post("/default/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    """
    - Creates new S3 bucket based off of UUID (from access_token),
    - and establishes a default album(directory),
    - and default image (default.jpg) in new bucket.
    """
    try:
        s3_credentials = await GalleryService.create_new_user_bucket(
            str(access_token), db
        )
        bucket_name = str(s3_credentials.get("bucket_name"))
        user_uuid = str(s3_credentials.get("user_uuid"))

        file_list = GalleryService.grab_file_list(
            bucket_name, user_uuid, album_name="default"
        )

        image_files = GalleryService.grab_image_files(
            file_list, bucket_name, album_name="default"
        )

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


@router.post("/upload/")
async def upload_image_to_gallery(
    file: UploadFile,
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    """
    - Uses User's UUID (from access_token) to upload new image
    - to user's bucket/default album.
    """
    try:
        await GalleryService.upload_new_image(str(access_token), file, db)
        # TODO: Utilize file meta data in s3 bucket
        #  print("file :=>", file)
        #  print("file.filename :=>", file.filename)
        #  print("file.content_type :=>", file.content_type)
        #  print("file.file :=>", file.file)

        return JSONResponse(status_code=200, content={"message": "HELLO WORLD!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
