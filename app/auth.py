"""Authentication and authorization helpers for role-based access control."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import session, redirect, url_for, flash, abort
from werkzeug.exceptions import Forbidden

from .models import User


def login_required(f: Callable) -> Callable:
    """Decorator to require user authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles: str) -> Callable:
    """Decorator to require specific role(s) for a route."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if user_id is None:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            user = User.query.get(user_id)
            if user is None or not user.is_active:
                session.clear()
                flash("Your account is not active. Please contact an administrator.", "danger")
                return redirect(url_for("auth.login"))
            
            if user.role not in allowed_roles:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def manager_required(f: Callable) -> Callable:
    """Decorator to require manager or superadmin role."""
    return role_required("manager", "superadmin")(f)


def get_current_user() -> User | None:
    """Get the currently logged-in user from session."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.query.get(user_id)


def can_access_entity(current_user: User, entity_type: str, entity_id: int) -> bool:
    """
    Check if current user can access a specific entity (customer/employee/portfolio).
    
    Args:
        current_user: The logged-in user
        entity_type: Type of entity ('customer', 'employee', or 'portfolio')
        entity_id: ID of the entity to check
        
    Returns:
        True if user can access, False otherwise
    """
    # Managers and superadmins can access everything
    if current_user.can_access_all():
        return True
    
    # Regular users and employees can only access their own data
    user_entity_id = current_user.get_entity_id()
    if user_entity_id is None:
        return False
    
    if entity_type == "customer":
        return current_user.c_id == entity_id
    elif entity_type == "employee":
        return current_user.e_id == entity_id
    elif entity_type == "portfolio":
        # For portfolios, check if it belongs to the user's customer or employee
        from .models import Portfolio
        portfolio = Portfolio.query.get(entity_id)
        if portfolio is None:
            return False
        if current_user.c_id is not None:
            return portfolio.c_id == current_user.c_id
        elif current_user.e_id is not None:
            return portfolio.e_id == current_user.e_id
        return False
    
    return False

