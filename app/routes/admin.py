from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.common.auth import admin_required, get_current_user
from app.common.user_helpers import delete_user_account
from extensions import db
from forms import ActionForm, AdminUserForm, ChangePasswordFormAdmin, TipForm
from models import Habit, Mood, Tip, ToDo, User

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_moods = Mood.query.count()
    total_tasks = ToDo.query.count()
    total_habits = Habit.query.count()
    total_tips = Tip.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_tips = Tip.query.order_by(Tip.updated_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        stats={
            "users": total_users,
            "moods": total_moods,
            "tasks": total_tasks,
            "habits": total_habits,
            "tips": total_tips,
        },
        recent_users=recent_users,
        recent_tips=recent_tips,
    )


@bp.route("/tips")
@admin_required
def tips():
    tips = Tip.query.order_by(Tip.created_at.desc()).all()
    action_form = ActionForm()
    return render_template("admin/tips.html", tips=tips, action_form=action_form)


@bp.route("/tips/new", methods=["GET", "POST"])
@admin_required
def tip_create():
    form = TipForm()
    if request.method == "POST" and form.validate_on_submit():
        tip = Tip(
            title=form.title.data,
            body=form.body.data,
            category=form.category.data or None,
            author=get_current_user(),
        )
        db.session.add(tip)
        db.session.commit()
        flash("Tip created", "success")
        return redirect(url_for("admin.tips"))
    return render_template("admin/tip_form.html", form=form, title="Add tip")


@bp.route("/tips/<int:tip_id>/edit", methods=["GET", "POST"])
@admin_required
def tip_edit(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    form = TipForm(obj=tip)
    if request.method == "POST" and form.validate_on_submit():
        tip.title = form.title.data
        tip.body = form.body.data
        tip.category = form.category.data or None
        db.session.commit()
        flash("Tip updated", "success")
        return redirect(url_for("admin.tips"))
    return render_template("admin/tip_form.html", form=form, title="Edit tip")


@bp.route("/tips/<int:tip_id>/delete", methods=["POST"])
@admin_required
def tip_delete(tip_id):
    form = ActionForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.tips"))
    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    flash("Tip deleted", "info")
    return redirect(url_for("admin.tips"))


@bp.route("/users")
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()

    role_forms = {u.id: AdminUserForm(obj=u) for u in users}
    action_forms = {u.id: ActionForm() for u in users}  # ban/unban/delete only
    password_forms = {u.id: ChangePasswordFormAdmin() for u in users}

    return render_template(
        "admin/users.html",
        users=users,
        role_forms=role_forms,
        action_forms=action_forms,
        password_forms=password_forms,
    )


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def user_role(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()
    if form.validate_on_submit():
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f"Updated role for {user.username}", "success")
    else:
        flash("Unable to update role", "danger")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/ban", methods=["POST"])
@admin_required
def user_ban(user_id):
    form = ActionForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot ban an admin user.", "warning")
        return redirect(url_for("admin.users"))
    user.is_banned = True
    db.session.commit()
    flash(f"Banned {user.username}", "info")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/unban", methods=["POST"])
@admin_required
def user_unban(user_id):
    form = ActionForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f"Unbanned {user.username}", "success")
    return redirect(url_for("admin.users"))

@bp.route("/users/<int:user_id>/change_password", methods=["POST"])
@admin_required
def user_change_password(user_id):
    user = User.query.get_or_404(user_id)

    if user.is_admin:
        flash("Cannot change password of an admin user.", "warning")
        return redirect(url_for("admin.users"))

    form = ChangePasswordFormAdmin()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.users"))

    user.set_password(form.new_password.data)
    db.session.commit()
    flash(f"Password changed for {user.username}", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def user_delete(user_id):
    form = ActionForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    current_user = get_current_user()
    if current_user and user.id == current_user.id:
        flash("You cannot delete your own account from the admin panel.", "danger")
        return redirect(url_for("admin.users"))
    delete_user_account(db, user)
    db.session.commit()
    flash(f"Deleted {user.username}", "info")
    return redirect(url_for("admin.users"))
