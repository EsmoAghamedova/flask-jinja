from functools import wraps

from flask import flash, g, redirect, request, session, url_for

from models import User


def get_current_user():
    if getattr(g, "_current_user", None) is not None:
        return g._current_user
    user = None
    if session.get("user_id"):
        user = User.query.get(session["user_id"])
        if user and getattr(user, "is_banned", False):
            session.clear()
            user = None
    g._current_user = user
    return user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            flash("You need admin rights to access that page.", "danger")
            return redirect(url_for("public.home"))
        return f(*args, **kwargs)

    return decorated_function


def register_auth_handlers(app):
    @app.context_processor
    def inject_auth_forms():
        from forms import LoginForm, SignupForm

        return dict(
            signup_form=SignupForm(),
            login_form=LoginForm(),
            current_user=get_current_user(),
        )

    @app.before_request
    def load_user():
        get_current_user()
