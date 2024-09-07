import hashlib
import io
import os
from typing import List

import boto3
from dotenv import load_dotenv
from fastapi import UploadFile

from .exception_handler_service import ExceptionService
from .security_service import SecurityService

load_dotenv()
AWS_REGION = str(os.environ.get("AWS_REGION"))


class S3Service:
    @staticmethod
    def get_s3_client():
        return boto3.client("s3")

    @staticmethod
    def get_bucket_index(user_uuid: str, num_buckets: int = 100) -> int:
        """
        - Takes a user's uuid and returns the number index
          that user's albums will live in.
        - NOTE: Returned index can only be number between 1 and 100
          (max number of S3 buckets allowed on AWS).
        """
        hash_digest = hashlib.sha256(user_uuid.encode()).hexdigest()
        return int(hash_digest, 16) % num_buckets

    @staticmethod
    def get_all_buckets() -> List[str]:
        """
        - Grabs All Existing Bucket Names from S3
        """
        try:
            s3_client = boto3.client("s3", region_name=AWS_REGION)
            response = s3_client.list_buckets()
            all_buckets = []
            if response:
                for bucket in response["Buckets"]:
                    all_buckets.append(bucket.get("Name"))
            return all_buckets
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return []

    @staticmethod
    def create_bucket(
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
            s3_client = boto3.client("s3", region_name=AWS_REGION)
            location = {"LocationConstraint": AWS_REGION}
            all_buckets = S3Service.get_all_buckets()
            if bucket_name not in all_buckets:
                s3_client.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration=location
                )
            s3_client.put_object(Bucket=bucket_name, Key=f"{user_uuid}/{album_name}/")
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    # TODO: Probably don't need to delete bucket ever,
    # but we WILL need to delete album
    @staticmethod
    def delete_bucket(bucket) -> None:
        try:
            s3_client = boto3.client("s3")
            s3_client.delete_bucket(Bucket=bucket)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    @staticmethod
    def grab_file_list(
        bucket: str, user_uuid: str, album_name: str = "default_album"
    ) -> List[str]:
        try:
            file_list = []
            s3 = boto3.client("s3")
            response = s3.list_objects_v2(
                Bucket=bucket, Prefix=f"{user_uuid}/{album_name}/"
            )
            if response:
                for contents in response["Contents"]:
                    key = contents["Key"]
                    if not key.endswith("/"):
                        file_list.append(key)
            return file_list
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return []

    @staticmethod
    def upload_file(
        file: UploadFile | None,
        bucket_name: str,
        user_uuid: str,
        object_name: str | None = None,
        file_name: str = "./src/pikoshi/public/default.webp",
        album_name: str = "default_album",
        file_data: io.BytesIO | None = None,
    ) -> None:
        """
        - Uploads a file to the user's uuid directory in the
          specified album_name (default if not defined)'.
        - If `file` parameter is defined, file is new file,
          and uses python-multipart's UploadFile object to upload
          to S3.
        - If `object_name` is defined, file is not defined and
          therefore default.webp is uploaded.
        - Otherwise, attempt is made to upload file without object
          or file specified.
        """
        try:
            s3_client = boto3.client("s3")

            gallery_name = f"{user_uuid}/{album_name}/"

            if file_data is not None and object_name is not None:
                object_name = os.path.join(gallery_name, object_name)
                return s3_client.upload_fileobj(file_data, bucket_name, object_name)

            if file is not None:
                object_name = os.path.join(
                    gallery_name, str(file.filename), str(file.filename)
                )
                return s3_client.upload_fileobj(file.file, bucket_name, object_name)

            if object_name is not None:
                object_name = os.path.join(
                    gallery_name,
                    os.path.basename(file_name),
                    os.path.basename(file_name),
                )
                return s3_client.upload_file(file_name, bucket_name, object_name)

            else:
                object_name = os.path.join(gallery_name, file_name, file_name)
                return s3_client.upload_fileobj(file_name, bucket_name, object_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    @staticmethod
    def download_file(file_name, bucket, object_name) -> None:
        try:
            s3_client = boto3.client("s3")
            s3_client.download_file(bucket, object_name, file_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    @staticmethod
    def delete_file(bucket, key_name) -> None:
        try:
            s3_client = boto3.client("s3")
            s3_client.delete_object(Bucket=bucket, Key=key_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
