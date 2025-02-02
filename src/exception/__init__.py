import sys
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """
    Organization: iNeuron Intelligence Private Limited
    AppException is customized exception class designed to capture refined details about exception
    such as python script file line number along with error message
    With custom exception one can easily spot source of error and provide quick fix.
    
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        extra: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(self.message)

    @staticmethod
    def error_message_detail(error: Exception, error_detail: sys):
        """
        error: Exception object raise from module
        error_detail: is sys module contains detail information about system execution information.
        """
        _, _, exc_tb = error_detail.exc_info()
        # extracting file name from exception traceback
        file_name = exc_tb.tb_frame.f_code.co_filename

        # preparing error message
        error_message = (
            f"Error occurred python script name [{file_name}]"
            f" line number [{exc_tb.tb_lineno}] error message [{error}]."
        )

        return error_message

    def __repr__(self):
        """
        Formating object of AppException
        """
        return AppException.__name__.__str__()

    def __str__(self):
        """
        Formating how a object should be visible if used in print statement.
        """
        return self.message

async def exception_handler(
    request: Request,
    exc: AppException
) -> JSONResponse:
    """Handle application exceptions"""
    logger.error(
        f"Exception occurred: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            **exc.extra
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.extra
        }
    )

class ValidationError(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str, extra: dict = None):
        super().__init__(message, status_code=400, extra=extra)

class AuthenticationError(AppException):
    """Raised when authentication fails"""
    def __init__(self, message: str, extra: dict = None):
        super().__init__(message, status_code=401, extra=extra)

class RateLimitError(AppException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, extra: dict = None):
        super().__init__(message, status_code=429, extra=extra)
