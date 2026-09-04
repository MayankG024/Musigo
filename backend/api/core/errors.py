"""Unified error schema and exception handlers"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import traceback
from api.core.config import settings

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None
    code: str | None = None
    status: int
    path: str | None = None


def http_exception_handler(request: Request, exc: HTTPException):
    payload = ErrorResponse(
        error=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        detail=None if isinstance(exc.detail, str) else str(exc.detail),
        code=getattr(exc, "error_code", None),
        status=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = ErrorResponse(
        error="ValidationError",
        detail=str(exc.errors()),
        code="validation_error",
        status=422,
        path=request.url.path,
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


def generic_exception_handler(request: Request, exc: Exception):
    detail = None
    if settings.DEBUG:
        detail = traceback.format_exc(limit=5)
    payload = ErrorResponse(
        error="InternalServerError",
        detail=detail,
        code="internal_error",
        status=500,
        path=request.url.path,
    )
    return JSONResponse(status_code=500, content=payload.model_dump())
