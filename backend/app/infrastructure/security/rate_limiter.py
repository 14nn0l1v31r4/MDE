try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    HAS_SLOWAPI = True
except ImportError:
    HAS_SLOWAPI = False

    class RateLimitExceeded(Exception):
        pass

    class MockLimiter:
        def limit(self, limit_value: str):
            def decorator(func):
                return func

            return decorator

    limiter = MockLimiter()

