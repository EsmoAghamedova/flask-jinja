import token
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from datetime import datetime

from app.routes import user
from app.utils import email
from extensions import db
from forms import LoginForm, ResetPasswordForm, SignupForm, ResendForm, ForgotPasswordForm
from models import User
from app.utils.tokens import generate_token, read_token
from app.utils.email import send_email

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

            email = form.email.data.strip().lower()
            username = form.username.data.strip()
            user = User(username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            token, _ = generate_token(user.id, "verify", expires_in=86400)
            verify_link = url_for("auth.verify", token=token, _external=True)
            print("VERIFY LINK:", verify_link)
            
            subject = "Verify your CalmSpace account"
            body = f"Welcome to CalmSpace! \n Please verify your email by clicking the link below: \n {verify_link} \n if you didn’t sign up, you can ignore this email."
            send_email(user.email, subject, body)
            
            flash("Account created! Check your email to verify, then log in.", "success")
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
                if not user.email_verified:
                    flash("Please verify your email first. Check your inbox", "info")
                    return redirect(url_for("auth.login"))
                session.clear()
                session["user_id"] = user.id
                flash("Logged in successfully", "success")
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                if user.is_admin:
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("user.dashboard"))
            flash("Invalid email or password", "danger")
        else:
            flash("Please correct the errors in the login form.", "danger")
    return render_template("public/login.html", form=form)

@bp.route("/verify")
def verify():
    token = request.args.get("token")

    if not token:
        flash("token is missing", "danger")
        return redirect(url_for("auth.login"))
    
    user_id = read_token(token, "verify")
    
    if not user_id:
        flash("user_id is missing", "danger")
        return redirect(url_for("auth.login"))
    
    user = User.query.get(user_id)

    if not user: 
        flash("User not found", "danger")
        return redirect(url_for("auth.login"))
    
    if user.email_verified:
        flash("Email already verified", "success")
        return redirect(url_for("auth.login"))
    
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()        
    db.session.commit()
        
    flash("Email verified successfully. You can now log in.", "success")
    return redirect(url_for("auth.login"))

# @bp.route("/resend-verification", methods=["POST"])
# def resend_verification():
#     email = request.form.get("email")
    
#     if not email:
#         flash("enter email")
#         return redirect(url_for("auth.login"))
    
#     user = User.query.filter_by(email=email).first()
    
#     if user and not user.email_verified:
#         token = generate_token(user.id, "verify", expires_in=86400)
#         verify_link = url_for("auth.verify", token=token, _external=True)
#         print("VERIFY LINK:", verify_link)
            
#         subject = "Verify your CalmSpace account"
#         body = f"Welcome to CalmSpace! \n Please verify your email by clicking the link below: \n {verify_link} \n if you didn’t sign up, you can ignore this email."
#         send_email(user.email, subject, body)
        
#         return redirect(url_for("auth.resend"))
    
#     flash("If that email exists, we sent a verification link.", "info")
#     return redirect(url_for("auth.login"))

@bp.route("/resend", methods=["GET", "POST"])
def resend():
    form = ResendForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
    
            if not email:
                flash("enter email")
                return redirect(url_for("auth.login"))
            
            user = User.query.filter_by(email=email).first()
            
            if user and not user.email_verified:
                token, _ = generate_token(user.id, "verify", expires_in=86400)
                verify_link = url_for("auth.verify", token=token, _external=True)
                print("VERIFY LINK:", verify_link)
                    
                subject = "Verify your CalmSpace account"
                body = f"Welcome to CalmSpace! \n Please verify your email by clicking the link below: \n {verify_link} \n if you didn’t sign up, you can ignore this email."
                send_email(user.email, subject, body)
                
                return redirect(url_for("auth.resend"))
            
            flash("If that email exists, we sent a verification link.", "info")
            return redirect(url_for("auth.login"))
        
        flash("Please correct the errors in the form.", "danger")

    return render_template("public/resend.html", form=form)

# @bp.route("/reset-password", methods=["GET", "POST"])
# def reset_password():
#     token = request.form.get("token")
#     if not token:
#         flash("token is missing", "danger")
#         return redirect(url_for("auth.login"))
    
#     user_id = read_token(token, "reset")
    
#     if not user_id:
#         flash("user_id is missing", "danger")
#         return redirect(url_for("auth.login"))
    
#     user = User.query.get(user_id)
    
#     if not user:
#         flash("User not found", "danger")
#         return redirect(url_for("auth.login"))
    
#     return render_template("public/reset_password.html", form=form, token=token)
    
    

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            user.password_reset_used_at = None
            db.session.commit()

            token, _ = generate_token(user.id, "reset", expires_in=600)  # ✅ FIX
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            subject = "Reset your password"
            body = (
                "You requested a password reset.\n\n"
                "This link expires in 10 minutes:\n"
                f"{reset_link}\n\n"
                "If you didn’t request this, you can ignore this email."
            )
            send_email(user.email, subject, body)

        flash("If that email exists, we sent a password reset link.", "info")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        flash("Please correct the errors in the form.", "danger")

    return render_template("public/forgot_password.html", form=form)

    
    

@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()

    if request.method == "GET":
        token = request.args.get("token")
    else:
        token = request.form.get("token")

    if not token:
        flash("Reset link is missing. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user_id = read_token(token, "reset")
    if not user_id:
        flash("Reset link is invalid or expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.get(user_id)
    if not user:
        flash("Reset link is invalid or expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if user.password_reset_used_at:
        flash("This reset link was already used. Please request a new one.", "info")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "GET":
        return render_template("public/reset_password.html", form=form, token=token)

    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.password_reset_used_at = datetime.utcnow()
        db.session.commit()

        flash("Password updated successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    flash("Please correct the errors in the form.", "danger")
    return render_template("public/reset_password.html", form=form, token=token)


    
@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))
