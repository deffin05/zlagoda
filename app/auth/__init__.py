from functools import wraps

from flask import Blueprint, abort
from flask_login import current_user

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

from app.auth import routes

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            elif current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator