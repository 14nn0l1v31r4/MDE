from dataclasses import dataclass


@dataclass(slots=True)
class RegisterUserDTO:
    email: str
    password: str
    full_name: str
    role: str = "analyst"


@dataclass(slots=True)
class LoginDTO:
    email: str
    password: str


@dataclass(slots=True)
class TokenDTO:
    access_token: str
    token_type: str = "bearer"


@dataclass(slots=True)
class UserResponseDTO:
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

