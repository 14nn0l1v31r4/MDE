import pytest
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError,
    UnauthorizedAccessError,
)
from app.application.dtos.auth_dtos import (
    RegisterUserDTO,
    LoginDTO,
    TokenDTO,
    UserResponseDTO,
)
from app.application.ports.repositories import UserRepository
from app.application.ports.security import PasswordHasher, TokenService
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import PyJWTSecurityTokenService
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.application.use_cases.get_current_user import GetCurrentUserUseCase


class InMemoryUserRepository:
    def __init__(self):
        self.users: dict[str, User] = {}

    def save(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for u in self.users.values():
            if u.email.lower() == email.lower():
                return u
        return None

    def list_all(self) -> list[User]:
        return list(self.users.values())


@pytest.fixture
def auth_setup():
    repo = InMemoryUserRepository()
    hasher: PasswordHasher = BcryptPasswordHasher(rounds=4)  # fast for tests
    token_service: TokenService = PyJWTSecurityTokenService(
        secret_key="secret_for_testing_purposes_only_32_chars",
        algorithm="HS256",
        expire_minutes=30,
    )
    return repo, hasher, token_service


def test_register_user_success(auth_setup):
    repo, hasher, token_service = auth_setup
    use_case = RegisterUserUseCase(repo, hasher)

    dto = RegisterUserDTO(
        email="prof@universidade.edu.br",
        password="Password123!",
        full_name="Prof. Carlos",
        role="analyst",
    )
    result = use_case.execute(dto)

    assert result.email == "prof@universidade.edu.br"
    assert result.full_name == "Prof. Carlos"
    assert result.role == "analyst"
    assert result.is_active is True
    assert result.id is not None

    # Password was hashed
    saved = repo.get_by_email("prof@universidade.edu.br")
    assert saved is not None
    assert saved.hashed_password != "Password123!"
    assert hasher.verify("Password123!", saved.hashed_password) is True


def test_register_user_duplicate_email(auth_setup):
    repo, hasher, token_service = auth_setup
    use_case = RegisterUserUseCase(repo, hasher)

    dto = RegisterUserDTO(
        email="duplicado@test.com",
        password="Password123!",
        full_name="User 1",
    )
    use_case.execute(dto)

    with pytest.raises(UserAlreadyExistsError, match="já cadastrado"):
        use_case.execute(dto)


def test_authenticate_user_success(auth_setup):
    repo, hasher, token_service = auth_setup
    reg_case = RegisterUserUseCase(repo, hasher)
    reg_case.execute(RegisterUserDTO("login@test.com", "SecretPass1", "Login User"))

    auth_case = AuthenticateUserUseCase(repo, hasher, token_service)
    token_dto = auth_case.execute(LoginDTO("login@test.com", "SecretPass1"))

    assert isinstance(token_dto, TokenDTO)
    assert token_dto.token_type == "bearer"
    assert token_dto.access_token is not None

    payload = token_service.decode_token(token_dto.access_token)
    assert payload["sub"] is not None
    assert payload["role"] == "analyst"


def test_authenticate_user_invalid_credentials(auth_setup):
    repo, hasher, token_service = auth_setup
    reg_case = RegisterUserUseCase(repo, hasher)
    reg_case.execute(RegisterUserDTO("user@test.com", "SecretPass1", "User"))

    auth_case = AuthenticateUserUseCase(repo, hasher, token_service)

    # Wrong email
    with pytest.raises(InvalidCredentialsError):
        auth_case.execute(LoginDTO("unknown@test.com", "SecretPass1"))

    # Wrong password
    with pytest.raises(InvalidCredentialsError):
        auth_case.execute(LoginDTO("user@test.com", "WrongPassword"))


def test_authenticate_user_inactive(auth_setup):
    repo, hasher, token_service = auth_setup
    reg_case = RegisterUserUseCase(repo, hasher)
    user_dto = reg_case.execute(RegisterUserDTO("inactive@test.com", "SecretPass1", "Inactive"))

    # Deactivate user
    user = repo.get_by_id(user_dto.id)
    user.is_active = False
    repo.save(user)

    auth_case = AuthenticateUserUseCase(repo, hasher, token_service)
    with pytest.raises(UserInactiveError, match="inativo"):
        auth_case.execute(LoginDTO("inactive@test.com", "SecretPass1"))


def test_get_current_user_use_case(auth_setup):
    repo, hasher, token_service = auth_setup
    reg_case = RegisterUserUseCase(repo, hasher)
    registered = reg_case.execute(RegisterUserDTO("me@test.com", "SecretPass1", "Me"))

    auth_case = AuthenticateUserUseCase(repo, hasher, token_service)
    token_dto = auth_case.execute(LoginDTO("me@test.com", "SecretPass1"))

    get_me = GetCurrentUserUseCase(repo, token_service)
    current_user = get_me.execute(token_dto.access_token)

    assert current_user.id == registered.id
    assert current_user.email == "me@test.com"
    assert current_user.is_active is True


def test_register_user_never_accepts_client_role(auth_setup):
    repo, hasher, _ = auth_setup
    use_case = RegisterUserUseCase(repo, hasher)

    result = use_case.execute(
        RegisterUserDTO(
            email="attacker@test.com",
            password="Password123!",
            full_name="Attacker",
            role="admin",
        )
    )

    assert result.role == "analyst"
    assert repo.get_by_email("attacker@test.com").role == "analyst"

