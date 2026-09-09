class DatasetNotFoundError(Exception):
    pass


class InvalidAnalysisInputError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserInactiveError(Exception):
    pass


class UnauthorizedAccessError(Exception):
    pass


class DatasetAccessForbiddenError(Exception):
    pass
