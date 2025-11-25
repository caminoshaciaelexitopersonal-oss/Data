from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

# Configuration for hardening
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_MIMETYPES = [
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "application/parquet",
    "application/zip",
    "application/gzip",
    "application/x-tar",
    "multipart/form-data",
]

class HardeningMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Apply hardening only to file upload endpoints
        if "upload" in request.url.path:
            content_length = request.headers.get("content-length")
            content_type = request.headers.get("content-type")

            # 1. Limit file sizes
            if content_length and int(content_length) > MAX_FILE_SIZE:
                return Response("File size exceeds the allowed limit.", status_code=413)

            # 2. Limit MIME types
            # This is a basic check; more robust validation happens in the service
            if content_type and not any(allowed in content_type for allowed in ALLOWED_MIMETYPES):
                 return Response(f"File type '{content_type}' is not allowed.", status_code=415)

        response = await call_next(request)
        return response
