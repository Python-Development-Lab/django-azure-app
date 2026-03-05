from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def require_group(group_name):
    """Restrict access to users belonging to a specific Entra ID group."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            groups = request.session.get('entra_groups', [])
            if group_name not in groups:
                return HttpResponseForbidden(
                    f"Access denied: group '{group_name}' required."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name):
    """Restrict access to users with a specific Entra ID app role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            roles = request.session.get('entra_roles', [])
            if role_name not in roles:
                return HttpResponseForbidden(
                    f"Access denied: role '{role_name}' required."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
