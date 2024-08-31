from fastapi import HTTPException
from fastapi.responses import JSONResponse
from jwt.exceptions import PyJWTError

from ..utils.logger import logger


class ExceptionService:
    @staticmethod
    def handle_http_exception(http_e: HTTPException) -> JSONResponse:
        logger.error(f"An error involving HTTP occurred: {str(http_e)}")
        return JSONResponse(
            status_code=http_e.status_code, content={"message": f"{http_e.detail}"}
        )

    @staticmethod
    def handle_jwt_exception(jwt_e: PyJWTError) -> JSONResponse:
        logger.error(f"An error involving JWT occurred: {str(jwt_e)}")
        return JSONResponse(
            status_code=401,
            content={"message": f"JWT error: {str(jwt_e)}"},
        )

    @staticmethod
    def handle_value_exception(ve: ValueError) -> JSONResponse:
        logger.error(f"Value error occurred: {str(ve)}")
        return JSONResponse(
            status_code=401,
            content={"message": str(ve)},
        )

    @staticmethod
    def handle_s3_exception(e: Exception) -> JSONResponse:
        logger.error(f"An error occurred while trying to access S3: {str(e)}")
        return JSONResponse(status_code=400, content={"message": f"S3 error: str{e}"})

    @staticmethod
    def handle_generic_exception(e: Exception) -> JSONResponse:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error."}
        )
