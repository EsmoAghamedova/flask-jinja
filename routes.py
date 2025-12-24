from collections import OrderedDict
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from extensions import db
from forms import AdminUserForm, HabitTrackerForm, LoginForm, MoodForm, SignupForm, TipForm, ToDoForm
from models import Habit, HabitEntry, Mood, Tip, ToDo, User

main = Blueprint("main", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("main.login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            flash("You need admin rights to access that page.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    if getattr(g, "_current_user", None) is not None:
        return g._current_user
    user = None
    if session.get("user_id"):
        user = User.query.get(session["user_id"])
    g._current_user = user
    return user


def get_user_stats(user_id):
    mood_count = Mood.query.filter_by(user_id=user_id).count()
    todo_done_count = ToDo.query.filter_by(user_id=user_id, done=True).count()
    habit_entries = HabitEntry.query.join(Habit).filter(Habit.user_id == user_id).count()
    return {
        "mood_count": mood_count,
        "todo_done_count": todo_done_count,
        "habit_entries": habit_entries,
    }


def get_badge_definitions():
    return [
        {
            "id": "mood_explorer",
            "name": "Mood Explorer",
            "desc": "Logged moods 5+ times",
            "emoji": "🧭",
            "check": lambda stats: stats["mood_count"] >= 5,
        },
        {
            "id": "task_slayer",
            "name": "Task Slayer",
            "desc": "Completed 10 tasks",
            "emoji": "✅",
            "check": lambda stats: stats["todo_done_count"] >= 10,
        },
        {
            "id": "habit_streak",
            "name": "Habit Streak",
            "desc": "Marked habits 7 times",
            "emoji": "🔥",
            "check": lambda stats: stats["habit_entries"] >= 7,
        },
        {
            "id": "consistency_pro",
            "name": "Consistency Pro",
            "desc": "Kept a strong routine",
            "emoji": "🏅",
            "check": lambda stats: stats["mood_count"] >= 20 and stats["todo_done_count"] >= 20,
        },
    ]


def calculate_badges(user_id):
    stats = get_user_stats(user_id)
    badges = []
    for badge in get_badge_definitions():
        if badge["check"](stats):
            badges.append({k: v for k, v in badge.items() if k != "check"})
    return badges


@main.context_processor
def inject_auth_forms():
    return dict(
        signup_form=SignupForm(),
        login_form=LoginForm(),
        current_user=get_current_user(),
    )


@main.before_app_request
def load_user():
    get_current_user()

@main.route("/")
def home():
    user = get_current_user()
    return render_template("home.html", user=user)


@main.route("/tips")
def tips():
    user = get_current_user()
    if user and user.is_admin:
        return redirect(url_for("main.admin_dashboard"))
    all_tips = Tip.query.order_by(Tip.created_at.desc()).all()
    return render_template("tips.html", tips=all_tips)


@main.route("/tip/<int:tip_id>")
def tip_detail(tip_id):
    user = get_current_user()
    if user and user.is_admin:
        return redirect(url_for("main.admin_dashboard"))
    tip = Tip.query.get_or_404(tip_id)
    return render_template("tip.html", tip=tip)

@main.route("/tracker")
@login_required  
def tracker():
    user = get_current_user()
    if user.is_admin:
        return redirect(url_for("main.admin_dashboard"))
    mood_count = Mood.query.filter_by(user_id=user.id).count()
    todo_count = ToDo.query.filter_by(user_id=user.id).count()
    todo_done_count = ToDo.query.filter_by(user_id=user.id, done=True).count()
    habit_count = Habit.query.filter_by(user_id=user.id).count()
    badges = calculate_badges(user.id)

    return render_template(
        "tracker.html",
        summary={
            "moods": mood_count,
            "todos": todo_count,
            "todos_done": todo_done_count,
            "habits": habit_count,
        },
        badges=badges,
    )


@main.route("/badges")
@login_required
def badges():
    user = get_current_user()
    if user.is_admin:
        return redirect(url_for("main.admin_dashboard"))
    stats = get_user_stats(user.id)
    all_badges = []
    for badge in get_badge_definitions():
        unlocked = badge["check"](stats)
        all_badges.append(
            {
                "id": badge["id"],
                "name": badge["name"],
                "desc": badge["desc"],
                "emoji": badge["emoji"],
                "unlocked": unlocked,
            }
        )
    return render_template("badges.html", badges=all_badges, stats=stats)

@main.route("/mood", methods=["GET", "POST"])
@login_required
def mood():
    user = get_current_user()
    mood_form = MoodForm()
    if request.method == "POST":
        if mood_form.validate_on_submit():
            new_mood = Mood(
                mood=mood_form.mood.data,
                notes=mood_form.notes.data,
                user_id=user.id,
            )
            db.session.add(new_mood)
            db.session.commit()
            flash("Mood logged.", "success")
            return redirect(url_for("main.mood"))
        else:
            flash("Please correct the errors in the form.", "danger")

    moods = (
        Mood.query.filter_by(user_id=user.id)
        .order_by(Mood.created_at.desc())
        .all()
    )
    return render_template("mood.html", mood_form=mood_form, moods=moods)


@main.route("/mood/edit/<int:mood_id>", methods=["GET", "POST"])
@login_required
def mood_edit(mood_id):
    user = get_current_user()
    mood_obj = Mood.query.get_or_404(mood_id)
    if mood_obj.user_id != user.id:
        flash("You are not authorized to edit that entry.", "danger")
        abort(403)
    mood_form = MoodForm(obj=mood_obj)
    if request.method == "POST":
        if mood_form.validate_on_submit():
            mood_obj.mood = mood_form.mood.data
            mood_obj.notes = mood_form.notes.data
            db.session.commit()
            flash("Mood updated.", "success")
            return redirect(url_for("main.mood"))
        else:
            flash("Please correct the errors in the form.", "danger")
    return render_template("mood_edit.html", mood_form=mood_form, mood=mood_obj)


@main.route("/mood/delete/<int:mood_id>", methods=["POST"])
@login_required
def mood_delete(mood_id):
    user = get_current_user()
    mood_obj = Mood.query.get_or_404(mood_id)
    if mood_obj.user_id != user.id:
        flash("You are not authorized to delete that entry.", "danger")
        abort(403)
    db.session.delete(mood_obj)
    db.session.commit()
    flash("Mood deleted.", "info")
    return redirect(url_for("main.mood"))

@main.route("/habit", methods=["GET", "POST"])
@login_required
def habit():
    user = get_current_user()
    habit_form = HabitTrackerForm()
    if request.method == "POST":
        if habit_form.validate_on_submit():
            new_habit = Habit(
                habit=habit_form.habit.data,
                frequency=habit_form.frequency.data,
                user_id=user.id,
            )
            db.session.add(new_habit)
            db.session.commit()
            flash("Habit added.", "success")
            return redirect(url_for("main.habit"))
        else:
            flash("Please correct the errors in the form.", "danger")

    habits = (
        Habit.query.filter_by(user_id=user.id)
        .order_by(Habit.created_at.desc())
        .all()
    )

    today = date.today()
    entries_today = HabitEntry.query.join(Habit).filter(
        Habit.user_id == user.id,
        HabitEntry.date == today,
    ).all()
    completed_today = set(e.habit_id for e in entries_today)

    return render_template(
        "habit.html", habit_form=habit_form, habits=habits, completed_today=completed_today
    )


@main.route("/habit/complete/<int:habit_id>", methods=["POST"])
@login_required
def habit_complete(habit_id):
    user = get_current_user()
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != user.id:
        flash("You are not authorized to modify that habit.", "danger")
        abort(403)

    today = date.today()
    existing = HabitEntry.query.filter_by(habit_id=habit_id, date=today).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Marked as not completed for today.", "info")
    else:
        entry = HabitEntry(habit_id=habit_id, date=today)
        db.session.add(entry)
        db.session.commit()
        flash("Marked completed for today.", "success")
    return redirect(url_for("main.habit"))


@main.route("/habit/edit/<int:habit_id>", methods=["GET", "POST"])
@login_required
def habit_edit(habit_id):
    user = get_current_user()
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != user.id:
        flash("You are not authorized to edit that habit.", "danger")
        abort(403)
    habit_form = HabitTrackerForm(obj=habit_obj)
    if request.method == "POST":
        if habit_form.validate_on_submit():
            habit_obj.habit = habit_form.habit.data
            habit_obj.frequency = habit_form.frequency.data
            db.session.commit()
            flash("Habit updated.", "success")
            return redirect(url_for("main.habit"))
        else:
            flash("Please correct the errors in the form.", "danger")
    return render_template("habit_edit.html", habit_form=habit_form, habit=habit_obj)


@main.route("/habit/delete/<int:habit_id>", methods=["POST"])
@login_required
def habit_delete(habit_id):
    user = get_current_user()
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != user.id:
        flash("You are not authorized to delete that habit.", "danger")
        abort(403)
    db.session.delete(habit_obj)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("main.habit"))


@main.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    user = get_current_user()
    todo_form = ToDoForm()
    if request.method == "POST":
        if todo_form.validate_on_submit():
            new_todo = ToDo(
                task=todo_form.task.data,
                detail=todo_form.detail.data,
                done=bool(todo_form.done.data),
                user_id=user.id,
            )
            db.session.add(new_todo)
            db.session.commit()
            flash("Task added.", "success")
            return redirect(url_for("main.todo"))
        else:
            flash("Please correct the errors in the form.", "danger")

    todos = (
        ToDo.query.filter_by(user_id=user.id)
        .order_by(ToDo.created_at.desc())
        .all()
    )
    return render_template("todo.html", todo_form=todo_form, todos=todos)


@main.route("/todo/edit/<int:todo_id>", methods=["GET", "POST"])
@login_required
def todo_edit(todo_id):
    user = get_current_user()
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != user.id:
        flash("You are not authorized to edit that task.", "danger")
        abort(403)
    todo_form = ToDoForm(obj=todo_obj)
    if request.method == "POST":
        if todo_form.validate_on_submit():
            todo_obj.task = todo_form.task.data
            todo_obj.detail = todo_form.detail.data
            todo_obj.done = bool(todo_form.done.data)
            db.session.commit()
            flash("Task updated.", "success")
            return redirect(url_for("main.todo"))
        else:
            flash("Please correct the errors in the form.", "danger")
    return render_template("todo_edit.html", todo_form=todo_form, todo=todo_obj)


@main.route("/todo/delete/<int:todo_id>", methods=["POST"])
@login_required
def todo_delete(todo_id):
    user = get_current_user()
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != user.id:
        flash("You are not authorized to delete that task.", "danger")
        abort(403)
    db.session.delete(todo_obj)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("main.todo"))

@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if request.method == "POST":
        if form.validate_on_submit():
            existing_user = User.query.filter(
                (User.email == form.email.data) | (User.username == form.username.data)
            ).first()
            if existing_user:
                flash("Username or email already registered", "danger")
                return redirect(url_for("main.signup"))

            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("main.login"))
        else:
            flash("Please correct the errors in the sign-up form.", "danger")
    return render_template("signup.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                session.clear()
                session["user_id"] = user.id
                flash("Logged in successfully", "success")
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                if user.is_admin:
                    return redirect(url_for("main.admin_dashboard"))
                return redirect(url_for("main.tracker"))
            flash("Invalid email or password", "danger")
        else:
            flash("Please correct the errors in the login form.", "danger")
    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@main.route("/progress")
@login_required
def progress():
    DAYS = 14
    user = get_current_user()
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=DAYS - 1)
    labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(DAYS)]

    moods_count = OrderedDict((label, 0) for label in labels)
    todos_done_count = OrderedDict((label, 0) for label in labels)
    habits_done_count = OrderedDict((label, 0) for label in labels)

    moods = Mood.query.filter(
        Mood.user_id == user.id,
        Mood.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for m in moods:
        key = m.created_at.date().strftime("%Y-%m-%d")
        if key in moods_count:
            moods_count[key] += 1

    todos = ToDo.query.filter(
        ToDo.user_id == user.id,
        ToDo.done.is_(True),
        ToDo.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for t in todos:
        key = t.created_at.date().strftime("%Y-%m-%d")
        if key in todos_done_count:
            todos_done_count[key] += 1

    habit_entries = HabitEntry.query.join(Habit).filter(
        Habit.user_id == user.id,
        HabitEntry.date >= start_date,
    ).all()
    for e in habit_entries:
        key = e.date.strftime("%Y-%m-%d")
        if key in habits_done_count:
            habits_done_count[key] += 1

    return render_template(
        "progress.html",
        labels=labels,
        moods_data=list(moods_count.values()),
        todos_data=list(todos_done_count.values()),
        habits_data=list(habits_done_count.values()),
        days=DAYS,
    )


@main.route("/admin")
@admin_required
def admin_dashboard():
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


@main.route("/admin/tips")
@admin_required
def admin_tips():
    tips = Tip.query.order_by(Tip.created_at.desc()).all()
    return render_template("admin/tips.html", tips=tips)


@main.route("/admin/tips/new", methods=["GET", "POST"])
@admin_required
def admin_tip_create():
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
        return redirect(url_for("main.admin_tips"))
    return render_template("admin/tip_form.html", form=form, title="Add tip")


@main.route("/admin/tips/<int:tip_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_tip_edit(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    form = TipForm(obj=tip)
    if request.method == "POST" and form.validate_on_submit():
        tip.title = form.title.data
        tip.body = form.body.data
        tip.category = form.category.data or None
        db.session.commit()
        flash("Tip updated", "success")
        return redirect(url_for("main.admin_tips"))
    return render_template("admin/tip_form.html", form=form, title="Edit tip")


@main.route("/admin/tips/<int:tip_id>/delete", methods=["POST"])
@admin_required
def admin_tip_delete(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    flash("Tip deleted", "info")
    return redirect(url_for("main.admin_tips"))


@main.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    forms = {user.id: AdminUserForm(obj=user) for user in users}
    return render_template("admin/users.html", users=users, forms=forms)


@main.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def admin_user_role(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()
    if form.validate_on_submit():
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f"Updated role for {user.username}", "success")
    else:
        flash("Unable to update role", "danger")
    return redirect(url_for("main.admin_users"))