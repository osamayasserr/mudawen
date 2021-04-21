from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


# Decorates view functions that require account confirmation
def requires_confirmation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.confirmed:
            flash('Please confirm your account.')
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)
    return wrapper


# Decorates view functions that require a certain permission
def requires_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorates view functions that require Admin permission
def admin_required(func):
    return requires_permission(Permission.ADMIN)(func)
