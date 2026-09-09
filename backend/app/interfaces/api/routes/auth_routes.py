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
from app.interfaces.api.dependencies import (
    get_current_active_user,
    password_hasher,
    token_service,
    user_repository,
)
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
    summary="Cadastrar novo usuário",
)
def register(request: UserRegisterRequest):
    use_case = RegisterUserUseCase(user_repository, password_hasher)
    dto = RegisterUserDTO(
        email=str(request.email),
        password=request.password,
        full_name=request.full_name,
        role=request.role,
    )
    try:
        saved = use_case.execute(dto)
        return UserResponse(
            id=saved.id,
            email=saved.email,
            full_name=saved.full_name,
            role=saved.role,
            is_active=saved.is_active,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticação de usuário e obtenção de token JWT",
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Suporta autenticação via formulário OAuth2 padrão (Swagger UI) e via JSON.
    """
    email = form_data.username
    password = form_data.password

    # Se chamado via JSON puro (Content-Type: application/json)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            email = body.get("email", email)
            password = body.get("password", password)
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe e-mail e senha para login",
        )

    use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)
    try:
        token_dto = use_case.execute(LoginDTO(email=email, password=password))
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login direto com payload JSON",
)
def login_json(request: UserLoginRequest):
    use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)
    try:
        token_dto = use_case.execute(LoginDTO(email=str(request.email), password=request.password))
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except UserInactiveError as e:
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

