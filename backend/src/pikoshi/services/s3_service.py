import os
from typing import List

import boto3

from .exception_handler_service import ExceptionService


class S3Service:
    @staticmethod
    def create_bucket(bucket_name, region=None) -> bool:
        try:
            if region is None:
                s3_client = boto3.client("s3")
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = boto3.client("s3", region_name=region)
                location = {"LocationConstraint": region}
                s3_client.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration=location
                )
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return False
        return True

    @staticmethod
    def delete_bucket(bucket) -> bool:
        s3_client = boto3.client("s3")
        try:
            s3_client.delete_bucket(Bucket=bucket)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return False
        return True

    @staticmethod
    def grab_file_list(bucket) -> List[str]:
        try:
            file_list = []
            s3 = boto3.client("s3")
            response = s3.list_objects_v2(Bucket=bucket)
            if response:
                for contents in response["Contents"]:
                    file_list.append(contents["Key"])
            return file_list
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return []

    @staticmethod
    def upload_file(file, bucket, object_name=None, gallery_name=None) -> bool:
        try:
            s3_client = boto3.client("s3")
            if gallery_name is None:
                gallery_name = "default/"
            # NOTE: If object_name is not NONE, then get file
            # from file-like object (direct upload)
            if object_name is not None:
                object_name = os.path.join(gallery_name, os.path.basename(file))
                s3_client.upload_file(file, bucket, object_name)
            # NOTE: Otherwise, get file from file system (hard drive)
            else:
                object_name = os.path.join(gallery_name, file.name)
                s3_client.upload_fileobj(file, bucket, object_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return False
        return True

    @staticmethod
    def download_file(file_name, bucket, object_name) -> bool:
        s3_client = boto3.client("s3")
        try:
            s3_client.download_file(bucket, object_name, file_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return False
        return True

    @staticmethod
    def delete_file(bucket, key_name) -> bool:
        s3_client = boto3.client("s3")
        try:
            s3_client.delete_object(Bucket=bucket, Key=key_name)
        except Exception as e:
            ExceptionService.handle_s3_exception(e)
            return False
        return True
