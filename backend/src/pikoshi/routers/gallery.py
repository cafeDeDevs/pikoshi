from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Cookie,
    Depends,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..middlewares.logger import TimedRoute
from ..services import exception_handler_service as ExceptionService
from ..services import gallery_service as GalleryService

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


# TODO: Figure out how to get parameters which will lead to the album name
# NOTE: IF parameter album_name == None, then default it to "default"
@router.post("/default-gallery/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """
    - Creates new S3 bucket based off of UUID (from access_token),
    - and establishes a default album(directory),
    - and default image (default.webp) in new bucket.
    """
    try:
        s3_credentials = await GalleryService.create_new_user_bucket(
            str(access_token), db_session
        )
        bucket_name = str(s3_credentials.get("bucket_name"))
        user_uuid = str(s3_credentials.get("user_uuid"))

        file_list = GalleryService.grab_file_list(
            bucket_name, user_uuid, album_name="default_album"
        )

        image_files = GalleryService.grab_image_files(
            file_list, bucket_name, album_name="default_album"
        )

        if len(image_files) == 0:
            raise HTTPException(
                status_code=400, detail="No Images Found In Default Album."
            )

        image_files = [img for img in image_files if img["type"] == "thumbnail"]

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


# TODO: again, pass from URL param that
@router.post("/default-single/")
async def grab_single_image(
    access_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
    body: dict = Body(...),
) -> Response:
    width = body.get("width", 0)
    file_name = body.get("file_name", "")

    s3_credentials = await GalleryService.grab_s3_credentials(
        str(access_token), db_session
    )
    bucket_name = str(s3_credentials.get("bucket_name"))
    user_uuid = str(s3_credentials.get("user_uuid"))

    image_files = GalleryService.grab_single_image(bucket_name, user_uuid, file_name)

    if len(image_files) == 0:
        raise HTTPException(status_code=400, detail="No Images Found In Default Album.")

    if len(file_name) == 0:
        raise HTTPException(status_code=400, detail="No file_name passed")

    if width < 768:
        image_file = next((img for img in image_files if img["type"] == "mobile"))
    else:
        image_file = next((img for img in image_files if img["type"] == "original"))

    if image_file is None:
        raise HTTPException(status_code=400, detail="No Image Found In Default Album.")

    return JSONResponse(
        status_code=200,
        content={
            "message": "Images Retrieved From S3 And Sent To Client Successfully.",
            "imageAsBase64": image_file,
        },
    )


@router.post("/upload/")
async def upload_image_to_gallery(
    file: UploadFile,
    access_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """
    - Uses User's UUID (from access_token) to upload new image
    - to user's bucket/default album.
    """
    try:
        await GalleryService.upload_new_image(str(access_token), file, db_session)

        return JSONResponse(
            status_code=200,
            content={"message": "New Image Uploaded To Album Successfully."},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
