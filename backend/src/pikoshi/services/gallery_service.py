import io
import os
from base64 import b64encode
from typing import Any, Dict, List, Tuple

from fastapi import Depends, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..utils.hashers import hash_string
from . import auth_service as AuthService
from . import exception_handler_service as ExceptionService
from . import s3_service as S3Service


async def create_new_user_bucket(
    access_token: str,
    db_session: AsyncSession = Depends(get_db_session),
) -> Dict[str, str]:
    """
    - Grabs the User data from the database using the JWT
      access_token's UUID.
    - Grabs the UUID from the returned User's data from the DB.
    - Hashes the User's UUID to determine which bucket index
      to put User's Account (UUID) in (can only be number between 1 and 100).
    - Establishes a bucket_name based off of returned index.
    - Creates a new bucket if it doesn't exist, otherwise simply proceeds
      with established bucket.
    - Establishes user's UUID as a directory within bucket (amounting to all
      of user's albums and images).
    - Returns a dictionary containing the User's bucket_name and user_uuid.
    """
    try:
        user = await AuthService.get_user_by_access_token(access_token, db_session)
        user_uuid = str(user.uuid)

        user_bucket_index = S3Service.get_bucket_index(user_uuid)  # type:ignore
        bucket_name = f"user-bucket-{user_bucket_index}"
        S3Service.create_bucket(bucket_name, user_uuid, album_name="default_album")
        return {"bucket_name": bucket_name, "user_uuid": user_uuid}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable To Create/Access User S3 Credentials: {e}",
        )


async def grab_s3_credentials(
    access_token: str, db_session: AsyncSession = Depends(get_db_session)
) -> Dict[str, str]:
    try:
        user = await AuthService.get_user_by_access_token(access_token, db_session)
        user_uuid = str(user.uuid)

        user_bucket_index = S3Service.get_bucket_index(user_uuid)  # type:ignore
        bucket_name = f"user-bucket-{user_bucket_index}"
        return {"bucket_name": bucket_name, "user_uuid": user_uuid}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable To Access User S3 Credentials: {e}",
        )


def grab_file_list(
    bucket_name: str,
    user_uuid: str,
    album_name: str = "default_album",
    max_keys: int = 90,
    continuation_token: str | None = None,
) -> dict[str, str | List[Any] | None]:
    """
    - Grabs The User's files within their '/default' Album.
    - If there are no files within the '/default' Album, upload the
      default.webp image from the '/public' directory.
    - Read the file_list again in case previous condition was True.
    - Return the file_list (so it can be rendered to Client).
    """
    try:
        s3_response = S3Service.grab_file_list(
            bucket_name, user_uuid, album_name, max_keys, continuation_token
        )

        file_list = s3_response["file_list"]

        if file_list is not None and len(file_list) == 0:
            upload_default_image(bucket_name, user_uuid)
            s3_response = S3Service.grab_file_list(
                bucket_name, user_uuid, album_name, max_keys, continuation_token
            )

        return {
            "file_list": s3_response["file_list"],
            "continuation_token": s3_response.get("continuation_token", None),
        }
    except Exception as e:
        ExceptionService.handle_generic_exception(e)
        return {
            "file_list": [],
            "continuation_token": None,
        }


def upload_default_image(
    bucket_name: str,
    user_uuid: str,
) -> None:
    """
    - Uploads the 'default.webp' image  and `mobile_default.webp`
      from the '/public' folder into the User's '/default' Album.
    """
    try:
        S3Service.upload_file(
            file=None,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name="default",
            file_name="./src/pikoshi/public/default.webp",
            album_name="default_album",
            file_data=None,
        )
        S3Service.upload_file(
            file=None,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name="default",
            file_name="./src/pikoshi/public/mobile_default.webp",
            album_name="default_album",
            file_data=None,
        )
        S3Service.upload_file(
            file=None,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name="default",
            file_name="./src/pikoshi/public/thumbnail_default.webp",
            album_name="default_album",
            file_data=None,
        )
    except Exception as e:
        ExceptionService.handle_generic_exception(e)


def grab_image_files(
    file_list, bucket_name: str, album_name: str = "default_album"
) -> List[dict]:
    """
    - Establishes an empty `image_files` list.
    - From the file_list array passed, check for if the path
      of all the files, the string: `/{album_name}/` exists.
      - If it does, then:
          - Grab all those files from the User's S3 bucket/UUID directory,
            convert them to Base64 encoded strings, and decode them as UTF-8.
          - And Append those newly encoded image strings to the `image_files`
            list.
    - Return the `image_files` list.
    """
    try:
        s3_client = S3Service.get_s3_client()
        image_files = []

        # TODO: Once album_name is grabbed from parameters, change this
        for file_name in file_list:
            if f"/{album_name}/" in file_name:
                orig_file_name = file_name.split("/")[-2]
                file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_name)
                image_data = b64encode(file_obj["Body"].read()).decode("utf-8")
                if "mobile" in file_name:
                    image_type = "mobile"
                elif "thumbnail" in file_name:
                    image_type = "thumbnail"
                else:
                    image_type = "original"
                image_files.append(
                    {
                        "data": image_data,
                        "type": image_type,
                        "file_name": orig_file_name,
                    }
                )

        return image_files
    except Exception as e:
        ExceptionService.handle_generic_exception(e)
        return []


def grab_single_image(
    bucket_name: str, user_uuid: str, file_name: str
) -> List[dict[str, str]]:
    orig_file_name = file_name
    prefix = f"{user_uuid}/default_album/{file_name}/"
    s3_client = S3Service.get_s3_client()
    result = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix, Delimiter="/")
    if "Contents" not in result:
        raise ValueError("No objects found by that file_name")
    images_as_base64 = []
    for obj in result["Contents"]:
        key = obj["Key"]

        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_content = s3_object["Body"].read()

        data = b64encode(file_content).decode("utf-8")
        file_name = key.split("/")[-1]
        if "mobile" in file_name:
            image_type = "mobile"
        elif "thumbnail" in file_name:
            image_type = "thumbnail"
        else:
            image_type = "original"

        images_as_base64.append(
            {"data": data, "file_name": orig_file_name, "type": image_type}
        )

    return images_as_base64


async def upload_new_image(
    access_token: str,
    file: UploadFile,
    db_session: AsyncSession = Depends(get_db_session),
    album_name: str = "default_album",
) -> None:
    """
    - Grabs the User data from the database using the JWT
      access_token's UUID.
    - Grabs the UUID from the returned User's data from the DB.
    - Hashes the User's UUID to determine which bucket index
      to put User's Account (UUID) in (can only be number between 1 and 100).
    - Establishes a bucket_name based off of returned index.
    - Uploads the image file to the User's appropriate
      bucket/UUID-directory/album-directory.
    - Establishes image_data in RAM via file.read() and io.BytesIO.
    - Uses _prepare_mobile_image() _private function to prepare mobile version of image.
    - Uploads the mobile image file to the User's appropriate
      bucket/UUID-directory/album-directory.
    """
    try:
        user = await AuthService.get_user_by_access_token(access_token, db_session)

        user_uuid = str(user.uuid)
        user_bucket_index = S3Service.get_bucket_index(user_uuid)
        bucket_name = f"user-bucket-{user_bucket_index}"

        # NOTE: file.seek() is necessary to read UploadFile from RAM again.
        # IMPORTANT: Do NOT reorder where these calls are in this function,
        # causes io errors.
        image_data = await file.read()
        image_bytes = io.BytesIO(image_data)
        await file.seek(0)

        # Uploads Desktop Image
        S3Service.upload_file(
            file=file,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name=None,
            album_name=album_name,
            file_data=None,
        )

        # Uploads Mobile Image
        mobile_size = (480, 320)
        mobile_data = await _resize_image(
            file, image_bytes, mobile_size, file_type="mobile"
        )
        img_bytes, object_name = mobile_data

        S3Service.upload_file(
            file=None,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name=object_name,
            album_name=album_name,
            file_data=img_bytes,
        )

        # Uploads Thumbnail Image
        thumbnail_size = (300, 200)
        thumbnail_data = await _resize_image(
            file, image_bytes, thumbnail_size, file_type="thumbnail"
        )
        img_bytes, object_name = thumbnail_data
        S3Service.upload_file(
            file=None,
            bucket_name=bucket_name,
            user_uuid=user_uuid,
            object_name=object_name,
            album_name=album_name,
            file_data=img_bytes,
        )

    except Exception as e:
        ExceptionService.handle_generic_exception(e)


async def _resize_image(
    file: UploadFile, image_bytes: io.BytesIO, size: Tuple[int, int], file_type: str
) -> Tuple[io.BytesIO, str]:
    """
    - Uses pillow's Image() to create mobile/thumbnail version of image in RAM.
    - Resizes image to mobile/thumbnail version.
    - Saves the image in .webp format.
    - Grabs the filename from the file object.
    - Hashes the filename.
    - Prepends `mobile` or `thumbnail` to the hashedfile name for file_name.
    - Prepares object_name based off of file_name.
    - Returns tuple of both img_bytes and object_name.
    """
    with Image.open(image_bytes) as img:
        img = img.copy()
        img.thumbnail(size)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="WEBP")
        img_bytes.seek(0)
        file_name = str(file.filename)
        hashed_file_name = hash_string(file_name)
        resized_file_name = f"{file_type}_{hashed_file_name}"
        object_name = os.path.join(file_name.split(".")[0], resized_file_name)
    return img_bytes, object_name
