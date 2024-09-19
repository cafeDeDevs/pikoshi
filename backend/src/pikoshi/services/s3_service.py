import hashlib
import io
import os
from typing import Any, List

from aiobotocore.session import get_session
from dotenv import load_dotenv
from fastapi import UploadFile

from ..utils.hashers import hash_string
from . import exception_handler_service as ExceptionService

load_dotenv()
AWS_REGION = str(os.environ.get("AWS_REGION"))
session = get_session()


def get_bucket_index(user_uuid: str, num_buckets: int = 100) -> int:
    """
    - Takes a user's uuid and returns the number index
      that user's albums will live in.
    - NOTE: Returned index can only be number between 1 and 100
      (max number of S3 buckets allowed on AWS).
    """
    hash_digest = hashlib.sha256(user_uuid.encode()).hexdigest()
    return int(hash_digest, 16) % num_buckets


async def get_all_buckets() -> List[str]:
    """
    - Grabs All Existing Bucket Names from S3
    """
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:
            response = await s3_client.list_buckets()
            all_buckets = []
            if response:
                for bucket in response["Buckets"]:
                    all_buckets.append(bucket.get("Name"))
            return all_buckets
    except Exception as e:
        ExceptionService.handle_s3_exception(e)
        return []


async def create_bucket(
    bucket_name: str,
    user_uuid: str,
    album_name: str,
) -> None:
    """
    - Grabs All Existing Bucket Names from S3
    - If Bucket Doesn't exist, we create a new bucket
      (name based off of hashed user's uuid).
    - Creates a new directory named after user's uuid
    - Creates a new album directory within user's uuid directory
    """
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:
            location = {"LocationConstraint": AWS_REGION}
            all_buckets = await get_all_buckets()
            if bucket_name not in all_buckets:
                await s3_client.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration=location
                )
                await s3_client.put_object(
                    Bucket=bucket_name, Key=f"{user_uuid}/{album_name}/"
                )
    except Exception as e:
        ExceptionService.handle_s3_exception(e)


# TODO: Probably don't need to delete bucket ever,
# but we WILL need to delete album
async def delete_bucket(bucket) -> None:
    try:
        async with session.create_client("s3") as s3_client:
            await s3_client.delete_bucket(Bucket=bucket)
    except Exception as e:
        ExceptionService.handle_s3_exception(e)


async def grab_file_list(
    bucket: str,
    user_uuid: str,
    album_name: str = "album_default",
    max_keys: int = 30,
    continuation_token: str | None = None,
    file_format: str = "thumbnail",
) -> dict[str, str | List[Any] | None]:
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:
            if continuation_token == "None":
                return {"file_list": None}
            file_list = []

            params = {
                "Bucket": bucket,
                "Prefix": f"{user_uuid}/{album_name}/{file_format}",
                "MaxKeys": max_keys,
            }

            if continuation_token is not None:
                params["ContinuationToken"] = continuation_token

            response = await s3_client.list_objects_v2(**params)

            if response and "Contents" in response:
                content_list = []
                for contents in response["Contents"]:
                    key = contents["Key"]
                    last_modified = contents["LastModified"]
                    if not key.endswith("/"):
                        content_list.append(
                            {"key": key, "last_modified": last_modified}
                        )

                content_list.sort(key=lambda x: x["last_modified"], reverse=True)
                file_list = [content["key"] for content in content_list]

            next_continuation_token = response.get("NextContinuationToken", None)

            return {
                "file_list": file_list,
                "continuation_token": next_continuation_token,
            }
    except Exception as e:
        ExceptionService.handle_s3_exception(e)
        return {
            "file_list": [],
            "continuation_token": None,
        }


async def upload_file(
    file: UploadFile | None,
    bucket_name: str,
    user_uuid: str,
    object_name: str | None = None,
    file_name: str = "./src/pikoshi/public/default.webp",
    album_name: str = "album_default",
    file_data: io.BytesIO | None = None,
    file_format: str = "thumbnail",
) -> None:
    # TODO: Refactor docstring once upload_new_image is refactored.
    """
    - Uploads a file to the user's uuid directory in the
      specified album_name (default if not defined)'.
    - If `file_data` parameter is defined, file is new MOBILE file,
      and works in conjunction with _prepare_mobile_image in
      GalleryService.
    - If `file` parameter is defined, file is new file,
      and uses python-multipart's UploadFile object to upload
      to S3.
    - If `object_name` is defined, file is not defined and
      therefore default.webp is uploaded.
    - Otherwise, attempt is made to upload file without object
      or file specified.
    """
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:

            gallery_name = f"{user_uuid}/{album_name}/{file_format}"

            # Mobile
            if file_data is not None and object_name is not None:
                file_data.seek(0)
                object_name = os.path.join(gallery_name, object_name)
                return await s3_client.put_object(
                    Bucket=bucket_name, Key=object_name, Body=file_data.read()
                )

            # New File
            elif file is not None:
                object_name = str(file.filename).split(".")[0]
                hashed_file_name = hash_string(str(file.filename))
                object_name = os.path.join(gallery_name, object_name, hashed_file_name)
                return await s3_client.put_object(
                    Bucket=bucket_name, Key=object_name, Body=await file.read()
                )

            # Default Files
            elif object_name is not None:
                with open(file_name, "rb") as f:
                    file_name = file_name.split("/")[-1]
                    hashed_file_name = hash_string(file_name)
                    object_name = os.path.join(
                        gallery_name,
                        os.path.basename(object_name),
                        os.path.basename(hashed_file_name),
                    )
                    return await s3_client.put_object(
                        Bucket=bucket_name, Key=object_name, Body=f.read()
                    )
            else:
                raise ValueError("Unknown Error Occurred When Uploading File(s).")
    except Exception as e:
        ExceptionService.handle_s3_exception(e)


async def download_file(file_name, bucket, object_name) -> None:
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:
            s3_client.download_file(bucket, object_name, file_name)
    except Exception as e:
        ExceptionService.handle_s3_exception(e)


async def delete_file(bucket, key_name) -> None:
    try:
        async with session.create_client("s3", region_name=AWS_REGION) as s3_client:
            s3_client.delete_object(Bucket=bucket, Key=key_name)
    except Exception as e:
        ExceptionService.handle_s3_exception(e)
