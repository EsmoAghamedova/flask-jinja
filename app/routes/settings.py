from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.common.auth import get_current_user, login_required
from app.common.user_helpers import delete_user_account, reset_user_progress
from extensions import db
from forms import DeleteAccountForm, PasswordChangeForm, ProfileForm, ResetProgressForm
from models import User

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/")
@login_required
def index():
    user = get_current_user()
    profile_form = ProfileForm(obj=user)
    password_form = PasswordChangeForm()
    reset_form = ResetProgressForm()
    delete_form = DeleteAccountForm()
    return render_template(
        "settings/index.html",
        profile_form=profile_form,
        password_form=password_form,
        reset_form=reset_form,
        delete_form=delete_form,
    )


@bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    user = get_current_user()
    profile_form = ProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.email.data != user.email:
            existing = User.query.filter_by(email=profile_form.email.data).first()
            if existing:
                flash("Email is already in use.", "danger")
                return redirect(url_for("settings.index"))
        if profile_form.username.data != user.username:
            existing = User.query.filter_by(username=profile_form.username.data).first()
            if existing:
                flash("Username is already in use.", "danger")
                return redirect(url_for("settings.index"))
        user.username = profile_form.username.data
        user.email = profile_form.email.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("settings.index"))

    flash("Please correct the errors in the profile form.", "danger")
    return redirect(url_for("settings.index"))


@bp.route("/password", methods=["POST"])
@login_required
def change_password():
    user = get_current_user()
    password_form = PasswordChangeForm()
    if password_form.validate_on_submit():
        if not user.check_password(password_form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("settings.index"))
        user.set_password(password_form.new_password.data)
        db.session.commit()
        flash("Password updated successfully.", "success")
        return redirect(url_for("settings.index"))

    flash("Please correct the errors in the password form.", "danger")
    return redirect(url_for("settings.index"))


@bp.route("/reset", methods=["POST"])
@login_required
def reset_progress():
    user = get_current_user()
    reset_form = ResetProgressForm()
    if reset_form.validate_on_submit():
        category = reset_form.category.data
        reset_user_progress(db, user, category)
        db.session.commit()
        if category == "all":
            flash("All progress has been reset.", "success")
        else:
            flash(f"Your {category} progress has been reset.", "success")
        return redirect(url_for("settings.index"))

    flash("Please confirm the reset before continuing.", "danger")
    return redirect(url_for("settings.index"))


@bp.route("/delete", methods=["POST"])
@login_required
def delete_account():
    user = get_current_user()
    delete_form = DeleteAccountForm()
    if delete_form.validate_on_submit():
        if not user.check_password(delete_form.password.data):
            flash("Password is incorrect.", "danger")
            return redirect(url_for("settings.index"))
        delete_user_account(db, user)
        db.session.commit()
        session.clear()
        flash("Your account has been deleted.", "info")
        return redirect(url_for("public.home"))

    flash("Please confirm account deletion.", "danger")
    return redirect(url_for("settings.index"))
