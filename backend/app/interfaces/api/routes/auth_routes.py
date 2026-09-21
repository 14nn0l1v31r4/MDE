from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.dtos.auth_dtos import LoginDTO, RegisterUserDTO
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from app.infrastructure.security.audit_logger import audit_request_event
from app.infrastructure.security.rate_limiter import limiter
from app.interfaces.api import dependencies as deps
from app.interfaces.api.dependencies import get_current_active_user
from app.interfaces.api.schemas.auth_schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário (Role sempre 'analyst')",
)
@limiter.limit("3/hour")
def register(request: Request, body: UserRegisterRequest):
    use_case = RegisterUserUseCase(deps.user_repository, deps.password_hasher)
    dto = RegisterUserDTO(
        email=str(body.email),
        password=body.password,
        full_name=body.full_name,
        role="analyst",
    )
    try:
        saved = use_case.execute(dto)
        audit_request_event(
            request,
            "auth.register",
            actor_user_id=saved.id,
            outcome="success",
        )
        return UserResponse(
            id=saved.id,
            email=saved.email,
            full_name=saved.full_name,
            role=saved.role,
            is_active=saved.is_active,
        )
    except UserAlreadyExistsError as e:
        audit_request_event(request, "auth.register", outcome="rejected")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticação de usuário via OAuth2 Password Form (Swagger)",
)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    use_case = AuthenticateUserUseCase(
        deps.user_repository,
        deps.password_hasher,
        deps.token_service,
    )
    try:
        token_dto = use_case.execute(
            LoginDTO(email=form_data.username, password=form_data.password)
        )
        audit_request_event(request, "auth.login", outcome="success")
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
        )
    except InvalidCredentialsError as e:
        audit_request_event(request, "auth.login", outcome="rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except UserInactiveError as e:
        audit_request_event(request, "auth.login", outcome="rejected")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login direto com payload JSON",
)
@limiter.limit("5/minute")
def login_json(request: Request, body: UserLoginRequest):
    use_case = AuthenticateUserUseCase(
        deps.user_repository,
        deps.password_hasher,
        deps.token_service,
    )
    try:
        token_dto = use_case.execute(
            LoginDTO(email=str(body.email), password=body.password)
        )
        audit_request_event(request, "auth.login_json", outcome="success")
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
        )
    except InvalidCredentialsError as e:
        audit_request_event(request, "auth.login_json", outcome="rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except UserInactiveError as e:
        audit_request_event(request, "auth.login_json", outcome="rejected")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter perfil do usuário atualmente autenticado",
)
def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
