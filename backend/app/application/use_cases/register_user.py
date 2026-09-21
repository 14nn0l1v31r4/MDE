from uuid import uuid4

from app.application.dtos.auth_dtos import RegisterUserDTO, UserResponseDTO
from app.application.ports.repositories import UserRepository
from app.application.ports.security import PasswordHasher
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import UserAlreadyExistsError


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        normalized_email = dto.email.strip().lower()
        existing = self.user_repository.get_by_email(normalized_email)
        if existing:
            raise UserAlreadyExistsError(f"Email {normalized_email} já cadastrado")

        hashed_password = self.password_hasher.hash(dto.password)
        # Public registration always assigns "analyst" role to prevent privilege escalation
        user = User(
            id=str(uuid4()),
            email=normalized_email,
            hashed_password=hashed_password,
            full_name=dto.full_name.strip(),
            role="analyst",
            is_active=True,
        )

        saved = self.user_repository.save(user)
        return UserResponseDTO(
            id=saved.id,
            email=saved.email,
            full_name=saved.full_name,
            role=saved.role,
            is_active=saved.is_active,
        )
