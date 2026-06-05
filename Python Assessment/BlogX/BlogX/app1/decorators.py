from django.contrib import messages
from django.shortcuts import redirect

from .models import User


def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have permission for this action.")
                return redirect("post_list")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


author_or_admin_required = role_required([User.Role.AUTHOR, User.Role.ADMIN])
