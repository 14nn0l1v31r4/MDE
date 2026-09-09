from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.domain.exceptions.domain_exceptions import (
    DatasetNotFoundError,
    InvalidAnalysisInputError,
    InvalidCredentialsError,
    UnauthorizedAccessError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from app.infrastructure.database.init_db import init_db
from app.infrastructure.security.rate_limiter import RateLimitExceeded, limiter
from app.interfaces.api.routes.analysis_routes import router as analysis_router
from app.interfaces.api.routes.auth_routes import router as auth_router
from app.interfaces.api.routes.dataset_routes import router as dataset_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    description="Educational Analytics API - Autenticação JWT Obrigatória e Isolamento de Dados",
)

# Estado do Rate Limiter
app.state.limiter = limiter

# CORS Seguro
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Rate Limit Exceeded Handler (HTTP 429)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Muitas requisições. Tente novamente mais tarde."},
    )


# Global Exception Handlers
@app.exception_handler(DatasetNotFoundError)
async def dataset_not_found_handler(request: Request, exc: DatasetNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(UnauthorizedAccessError)
async def unauthorized_handler(request: Request, exc: UnauthorizedAccessError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(UserInactiveError)
async def user_inactive_handler(request: Request, exc: UserInactiveError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidAnalysisInputError)
async def invalid_analysis_handler(request: Request, exc: InvalidAnalysisInputError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


# Rotas
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(dataset_router, prefix=settings.api_prefix)
app.include_router(analysis_router, prefix=settings.api_prefix)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
