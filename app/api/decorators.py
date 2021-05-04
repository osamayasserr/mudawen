from functools import wraps
from flask import g
from .errors import forbidden


def requires_permission(permission):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return function(*args, **kwargs)
        return wrapper
    return decorator
