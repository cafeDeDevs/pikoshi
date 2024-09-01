from base64 import b64encode
from typing import Dict, List

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services.jwt_service import JWTAuthService
from ..services.s3_service import S3Service
from .exception_handler_service import ExceptionService
from .s3_service import S3Service
from .user_service import get_user_by_uuid


class GalleryService:
    @staticmethod
    async def create_new_user_bucket(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> Dict[str, str]:
        try:
            # TODO: put this logic in single auth service helper func
            # NOTE: Look for other repeated instances of this logic
            verified_token = JWTAuthService.verify_token(access_token)
            user_uuid = verified_token.get("sub")  # type:ignore
            user = get_user_by_uuid(db, user_uuid)
            user_uuid = str(user.uuid)

            user_bucket_index = S3Service.get_bucket_index(user_uuid)  # type:ignore
            bucket_name = f"user-bucket-{user_bucket_index}"
            S3Service.create_bucket(bucket_name, user_uuid, album_name="default")
            return {"bucket_name": bucket_name, "user_uuid": user_uuid}
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable To Create/Access User S3 Credentials: {e}",
            )

    @staticmethod
    def grab_file_list(
        bucket_name: str, user_uuid: str, album_name: str = "default"
    ) -> List[str]:
        try:
            file_list = S3Service.grab_file_list(bucket_name, user_uuid)

            if len(file_list) == 0:
                GalleryService.upload_default_image(bucket_name, user_uuid)

            file_list = S3Service.grab_file_list(
                bucket_name, user_uuid, album_name=album_name
            )

            return file_list
        except Exception as e:
            ExceptionService.handle_generic_exception(e)
            return []

    @staticmethod
    def upload_default_image(
        bucket_name: str,
        user_uuid: str,
    ) -> None:
        try:
            S3Service.upload_file(
                file=None,
                bucket_name=bucket_name,
                user_uuid=user_uuid,
                object_name="default.jpg",
                file_name="./src/pikoshi/public/default.jpg",
                album_name="default",
            )
        except Exception as e:
            ExceptionService.handle_generic_exception(e)

    @staticmethod
    def grab_image_files(
        file_list, bucket_name: str, album_name: str = "default"
    ) -> List[str]:
        try:
            s3_client = S3Service.get_s3_client()
            image_files = []

            # TODO: Once album_name is grabbed from parameters, change this
            for file_name in file_list:
                if f"/{album_name}/" in file_name:
                    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_name)
                    image_data = b64encode(file_obj["Body"].read()).decode("utf-8")
                    image_files.append(image_data)

            return image_files
        except Exception as e:
            ExceptionService.handle_generic_exception(e)
            return []

    @staticmethod
    async def upload_new_image(
        access_token: str,
        file: UploadFile,
        db: Session = Depends(get_db),
        album_name: str = "default",
    ) -> None:
        try:
            verified_token = JWTAuthService.verify_token(access_token)
            user_uuid = verified_token.get("sub")  # type:ignore
            user = get_user_by_uuid(db, user_uuid)

            user_uuid = str(user.uuid)
            user_bucket_index = S3Service.get_bucket_index(user_uuid)
            bucket_name = f"user-bucket-{user_bucket_index}"

            S3Service.upload_file(
                file=file,
                bucket_name=bucket_name,
                user_uuid=user_uuid,
                object_name=None,
                album_name=album_name,
            )
        except Exception as e:
            ExceptionService.handle_generic_exception(e)
