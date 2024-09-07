from base64 import b64encode
from typing import Dict, List

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services.auth_service import AuthService
from ..services.s3_service import S3Service
from .exception_handler_service import ExceptionService
from .s3_service import S3Service


class GalleryService:
    @staticmethod
    async def create_new_user_bucket(
        access_token: str,
        db: Session = Depends(get_db),
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
            user = AuthService.get_user_by_access_token(access_token, db)
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

    @staticmethod
    def grab_file_list(
        bucket_name: str, user_uuid: str, album_name: str = "default_album"
    ) -> List[str]:
        """
        - Grabs The User's files within their '/default' Album.
        - If there are no files within the '/default' Album, upload the
          default.webp image from the '/public' directory.
        - Read the file_list again in case previous condition was True.
        - Return the file_list (so it can be rendered to Client).
        """
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
        """
        - Uploads the 'default.webp' image from the '/public' folder
          into the User's '/default' Album.
        """
        try:
            S3Service.upload_file(
                file=None,
                bucket_name=bucket_name,
                user_uuid=user_uuid,
                object_name="default.webp",
                file_name="./src/pikoshi/public/default.webp",
                album_name="default_album",
            )
        except Exception as e:
            ExceptionService.handle_generic_exception(e)

    @staticmethod
    def grab_image_files(
        file_list, bucket_name: str, album_name: str = "default_album"
    ) -> List[str]:
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
        album_name: str = "default_album",
    ) -> None:
        """
        - Grabs the User data from the database using the JWT
          access_token's UUID.
        - Grabs the UUID from the returned User's data from the DB.
        - Hashes the User's UUID to determine which bucket index
          to put User's Account (UUID) in (can only be number between 1 and 100).
        - Establishes a bucket_name based off of returned index.
        - Uploads the file to the User's appropriate
          bucket/UUID-directory/album-directory.
        """
        try:
            user = AuthService.get_user_by_access_token(access_token, db)

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
