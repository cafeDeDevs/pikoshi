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
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..middlewares.logger import TimedRoute
from ..services import exception_handler_service as ExceptionService
from ..services import gallery_service as GalleryService
from ..utils.auth_cookies import set_s3_continuation_token

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


# TODO: Figure out how to get parameters which will lead to the album name
# NOTE: IF parameter album_name == None, then default it to "default"
@router.post("/image-count/")
async def get_default_image_count(
    access_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
    s3_continuation_token: Annotated[str | None, Cookie()] = None,
    max_keys: int = 30,
    file_format: str = "thumbnail",
) -> Response:
    try:
        s3_credentials = await GalleryService.grab_s3_credentials(
            str(access_token), db_session
        )
        bucket_name = str(s3_credentials.get("bucket_name"))
        user_uuid = str(s3_credentials.get("user_uuid"))
        s3_response = await GalleryService.grab_file_list(
            bucket_name,
            user_uuid,
            album_name="album_default",
            max_keys=max_keys,
            continuation_token=s3_continuation_token,
            file_format=file_format,
        )
        file_list = s3_response["file_list"]
        if file_list is None:
            return JSONResponse(
                status_code=204,
                content={"message": "No more images in this album.", "image_count": 0},
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Successfully retrieved number of images remaining",
                "image_count": len(file_list),
            },
        )
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except Exception as e:
        return ExceptionService.handle_s3_exception(e)


# TODO: Figure out how to get parameters which will lead to the album name
# NOTE: IF parameter album_name == None, then default it to "default"
@router.post("/default-gallery/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
    s3_continuation_token: Annotated[str | None, Cookie()] = None,
    max_keys: int = 30,
    file_format: str = "thumbnail",
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

        s3_response = await GalleryService.grab_file_list(
            bucket_name,
            user_uuid,
            album_name="album_default",
            max_keys=max_keys,
            continuation_token=s3_continuation_token,
            file_format=file_format,
        )

        file_list = s3_response["file_list"]
        next_token = str(s3_response["continuation_token"])

        boundary = GalleryService.generate_unique_boundary()
        image_files = GalleryService.grab_image_files(
            file_list,
            bucket_name,
            boundary,
            album_name="album_default",
            file_format=file_format,
        )

        response = StreamingResponse(
            image_files,
            media_type="application/octet-stream",
            headers={
                "X-Boundary": str(boundary),
            },
        )

        response = set_s3_continuation_token(response, next_token)
        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except Exception as e:
        return ExceptionService.handle_s3_exception(e)


@router.post("/default-load-more/")
async def load_next_page_of_images(
    access_token: Annotated[str | None, Cookie()] = None,
    s3_continuation_token: Annotated[str | None, Cookie()] = None,
    db_session: AsyncSession = Depends(get_db_session),
    max_keys: int = 30,
    file_format="thumbnail",
) -> Response:
    try:
        s3_credentials = await GalleryService.create_new_user_bucket(
            str(access_token), db_session
        )
        bucket_name = str(s3_credentials.get("bucket_name"))
        user_uuid = str(s3_credentials.get("user_uuid"))

        s3_response = await GalleryService.grab_file_list(
            bucket_name,
            user_uuid,
            album_name="album_default",
            max_keys=max_keys,
            continuation_token=s3_continuation_token,
            file_format=file_format,
        )

        file_list = s3_response["file_list"]
        next_token = str(s3_response["continuation_token"])
        if next_token is None:
            return JSONResponse(
                status_code=204, content={"message": "No More Images Available To Load"}
            )

        boundary = GalleryService.generate_unique_boundary()
        image_files = GalleryService.grab_image_files(
            file_list,
            bucket_name,
            boundary,
            album_name="album_default",
            file_format=file_format,
        )

        response = StreamingResponse(
            image_files,
            media_type="application/octet-stream",
            headers={
                "X-Boundary": str(boundary),
            },
        )

        response = set_s3_continuation_token(response, next_token)
        return response
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
    try:
        width = body.get("width", 0)
        file_name = body.get("file_name", "")
        file_format = "mobile" if width < 768 else "original"

        s3_credentials = await GalleryService.grab_s3_credentials(
            str(access_token), db_session
        )
        bucket_name = str(s3_credentials.get("bucket_name"))
        user_uuid = str(s3_credentials.get("user_uuid"))

        image_file = await GalleryService.grab_single_image(
            bucket_name, user_uuid, file_name, file_format=file_format
        )

        if image_file is False:
            raise HTTPException(
                status_code=400, detail="No Image Found In Default Album."
            )

        if len(file_name) == 0:
            raise HTTPException(status_code=400, detail="No file_name passed")

        return JSONResponse(
            status_code=200,
            content={
                "message": "Images Retrieved From S3 And Sent To Client Successfully.",
                "imageAsBase64": image_file,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
