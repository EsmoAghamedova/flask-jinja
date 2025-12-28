from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from extensions import db
from forms import LoginForm, SignupForm
from models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if request.method == "POST":
        if form.validate_on_submit():
            existing_user = User.query.filter(
                (User.email == form.email.data) | (User.username == form.username.data)
            ).first()
            if existing_user:
                flash("Username or email already registered", "danger")
                return redirect(url_for("auth.signup"))

            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
        flash("Please correct the errors in the sign-up form.", "danger")
    return render_template("public/signup.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                if getattr(user, "is_banned", False):
                    flash("Your account is banned. Contact support.", "danger")
                    return redirect(url_for("auth.login"))
                session.clear()
                session["user_id"] = user.id
                flash("Logged in successfully", "success")
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                if user.is_admin:
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("user.tracker"))
            flash("Invalid email or password", "danger")
        else:
            flash("Please correct the errors in the login form.", "danger")
    return render_template("public/login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))
