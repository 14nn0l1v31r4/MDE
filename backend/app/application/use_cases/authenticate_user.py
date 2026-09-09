from app.application.dtos.auth_dtos import LoginDTO, TokenDTO
from app.application.ports.repositories import UserRepository
from app.application.ports.security import PasswordHasher, TokenService
from app.domain.exceptions.domain_exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
)


class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, dto: LoginDTO) -> TokenDTO:
        normalized_email = dto.email.strip().lower()
        user = self.user_repository.get_by_email(normalized_email)
        if not user or not self.password_hasher.verify(dto.password, user.hashed_password):
            raise InvalidCredentialsError("E-mail ou senha incorretos")

        if not user.is_active:
            raise UserInactiveError("Usuário inativo. Contate o administrador.")

        token = self.token_service.create_access_token({
            "sub": user.id,
            "email": user.email,
            "role": user.role,
        })

        return TokenDTO(access_token=token, token_type="bearer")

