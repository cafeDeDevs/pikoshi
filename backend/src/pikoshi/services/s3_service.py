import hashlib
import os
from typing import List

import boto3
from dotenv import load_dotenv
from fastapi import UploadFile

from .exception_handler_service import ExceptionService

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
    def create_bucket(
        bucket_name: str,
        user_uuid: str,
        album_name: str,
    ) -> None:
        try:
            s3_client = boto3.client("s3", region_name=AWS_REGION)
            location = {"LocationConstraint": AWS_REGION}
            s3_client.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=location
            )
            s3_client.put_object(Bucket=bucket_name, Key=f"{user_uuid}/{album_name}/")
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    @staticmethod
    def delete_bucket(bucket) -> None:
        try:
            s3_client = boto3.client("s3")
            s3_client.delete_bucket(Bucket=bucket)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)

    @staticmethod
    def grab_file_list(
        bucket: str, user_uuid: str, album_name: str = "default"
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
        album_name: str = "default",
    ) -> None:
        try:
            s3_client = boto3.client("s3")

            gallery_name = f"{user_uuid}/{album_name}/"

            if file is not None:
                object_name = os.path.join(gallery_name, str(file.filename))
                return s3_client.upload_fileobj(file.file, bucket_name, object_name)

            if object_name is not None:
                object_name = os.path.join(gallery_name, os.path.basename(file_name))
                return s3_client.upload_file(file_name, bucket_name, object_name)

            else:
                object_name = os.path.join(gallery_name, file_name)
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
