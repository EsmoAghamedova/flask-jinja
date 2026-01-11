from flask import Blueprint, redirect, render_template, url_for

from app.common.auth import get_current_user
from models import Tip

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    user = get_current_user()
    if user and user.is_admin:
        return redirect(url_for("admin.dashboard"))
    if user:
        return redirect(url_for("user.dashboard"))
    return render_template("public/home.html", user=user)


@bp.route("/tips")
def tips():
    user = get_current_user()
    if user and user.is_admin:
        return redirect(url_for("admin.dashboard"))
    all_tips = Tip.query.order_by(Tip.created_at.desc()).all()
    return render_template("public/tips.html", tips=all_tips)


@bp.route("/tip/<int:tip_id>")
def tip_detail(tip_id):
    user = get_current_user()
    if user and user.is_admin:
        return redirect(url_for("admin.dashboard"))
    tip = Tip.query.get_or_404(tip_id)
    return render_template("public/tip.html", tip=tip)
