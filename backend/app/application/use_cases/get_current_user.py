from app.application.ports.repositories import UserRepository
from app.application.ports.security import TokenService
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    UnauthorizedAccessError,
    UserInactiveError,
)


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository, token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    def execute(self, token: str) -> User:
        payload = self.token_service.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedAccessError("Token inválido: identificador de usuário ausente")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedAccessError("Usuário associado ao token não encontrado")

        if not user.is_active:
            raise UserInactiveError("Usuário inativo")

        return user

