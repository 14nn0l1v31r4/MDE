import bcrypt


class BcryptPasswordHasher:
    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_bytes.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

