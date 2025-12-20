from collections import OrderedDict
from datetime import datetime, timedelta, date
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    abort,
)
from extensions import db
from forms import (
    MoodForm,
    ToDoForm,
    HabitTrackerForm,
    SignupForm,
    LoginForm,
)
from models import Mood, ToDo, Habit, User, HabitEntry

main = Blueprint("main", __name__)

# -----------------------
# Static data
# -----------------------
TIPS_LIST = [
    {"title": "🧘‍♀️ Meditation", "text": "Spend 5–10 minutes focusing on your breath."},
    {"title": "🌿 Nature Walks", "text": "Take a walk outside to clear your mind."},
    {"title": "📓 Journaling", "text": "Write down your thoughts and gratitude."},
    {"title": "💧 Hydration", "text": "Drink enough water daily."},
    {"title": "🛌 Sleep Routine", "text": "Go to bed and wake up at consistent times."},
    {"title": "🎵 Music Breaks", "text": "Listen to calming music to recharge."},
]


# -----------------------
# Helpers / auth
# -----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("main.login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


@main.context_processor
def inject_auth_forms():
    """
    Provide signup/login forms to all templates to avoid collisions with page-specific
    form variable names (mood_form, todo_form, habit_form).
    """
    return dict(signup_form=SignupForm(), login_form=LoginForm())


# -----------------------
# Static/simple pages
# -----------------------
@main.route("/")
def home():
    user = None
    if session.get("user_id"):
        user = User.query.get(session["user_id"])
    return render_template("home.html", user=user)


@main.route("/tips")
def tips():
    # Endpoint name will be 'main.tips' because blueprint is 'main' and function is 'tips'
    return render_template("tips.html", tips=TIPS_LIST)


@main.route("/tip/<int:tip_id>")
def tip_detail(tip_id):
    if tip_id < 0 or tip_id >= len(TIPS_LIST):
        abort(404)
    return render_template("tip.html", tip=TIPS_LIST[tip_id])


# -----------------------
# Tracker dashboard
# -----------------------
@main.route("/tracker")
@login_required
def tracker():
    return render_template("tracker.html")


# -----------------------
# Mood CRUD
# -----------------------
@main.route("/mood", methods=["GET", "POST"])
@login_required
def mood():
    mood_form = MoodForm()
    if request.method == "POST":
        if mood_form.validate_on_submit():
            new_mood = Mood(
                mood=mood_form.mood.data,
                notes=mood_form.notes.data,
                user_id=session["user_id"],
            )
            db.session.add(new_mood)
            db.session.commit()
            flash("Mood logged.", "success")
            return redirect(url_for("main.mood"))
        else:
            flash("Please correct the errors in the form.", "danger")

    moods = (
        Mood.query.filter_by(user_id=session["user_id"])
        .order_by(Mood.created_at.desc())
        .all()
    )
    return render_template("mood.html", mood_form=mood_form, moods=moods)


@main.route("/mood/edit/<int:mood_id>", methods=["GET", "POST"])
@login_required
def mood_edit(mood_id):
    mood_obj = Mood.query.get_or_404(mood_id)
    if mood_obj.user_id != session["user_id"]:
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
    mood_obj = Mood.query.get_or_404(mood_id)
    if mood_obj.user_id != session["user_id"]:
        flash("You are not authorized to delete that entry.", "danger")
        abort(403)
    db.session.delete(mood_obj)
    db.session.commit()
    flash("Mood deleted.", "info")
    return redirect(url_for("main.mood"))


# -----------------------
# Habit CRUD + per-day completion
# -----------------------
@main.route("/habit", methods=["GET", "POST"])
@login_required
def habit():
    habit_form = HabitTrackerForm()
    if request.method == "POST":
        if habit_form.validate_on_submit():
            new_habit = Habit(
                habit=habit_form.habit.data,
                frequency=habit_form.frequency.data,
                user_id=session["user_id"],
            )
            db.session.add(new_habit)
            db.session.commit()
            flash("Habit added.", "success")
            return redirect(url_for("main.habit"))
        else:
            flash("Please correct the errors in the form.", "danger")

    habits = (
        Habit.query.filter_by(user_id=session["user_id"])
        .order_by(Habit.created_at.desc())
        .all()
    )

    today = date.today()
    entries_today = HabitEntry.query.join(Habit).filter(
        Habit.user_id == session["user_id"],
        HabitEntry.date == today,
    ).all()
    completed_today = set(e.habit_id for e in entries_today)

    return render_template(
        "habit.html", habit_form=habit_form, habits=habits, completed_today=completed_today
    )


@main.route("/habit/complete/<int:habit_id>", methods=["POST"])
@login_required
def habit_complete(habit_id):
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != session["user_id"]:
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
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != session["user_id"]:
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
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != session["user_id"]:
        flash("You are not authorized to delete that habit.", "danger")
        abort(403)
    db.session.delete(habit_obj)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("main.habit"))


# -----------------------
# ToDo CRUD
# -----------------------
@main.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    todo_form = ToDoForm()
    if request.method == "POST":
        if todo_form.validate_on_submit():
            new_todo = ToDo(
                task=todo_form.task.data,
                detail=todo_form.detail.data,
                done=bool(todo_form.done.data),
                user_id=session["user_id"],
            )
            db.session.add(new_todo)
            db.session.commit()
            flash("Task added.", "success")
            return redirect(url_for("main.todo"))
        else:
            flash("Please correct the errors in the form.", "danger")

    todos = (
        ToDo.query.filter_by(user_id=session["user_id"])
        .order_by(ToDo.created_at.desc())
        .all()
    )
    return render_template("todo.html", todo_form=todo_form, todos=todos)


@main.route("/todo/edit/<int:todo_id>", methods=["GET", "POST"])
@login_required
def todo_edit(todo_id):
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != session["user_id"]:
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
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != session["user_id"]:
        flash("You are not authorized to delete that task.", "danger")
        abort(403)
    db.session.delete(todo_obj)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("main.todo"))


# -----------------------
# Auth: signup / login / logout
# -----------------------
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


# -----------------------
# Progress charts
# -----------------------
@main.route("/progress")
@login_required
def progress():
    DAYS = 14
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=DAYS - 1)
    labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(DAYS)]

    moods_count = OrderedDict((label, 0) for label in labels)
    todos_done_count = OrderedDict((label, 0) for label in labels)
    habits_done_count = OrderedDict((label, 0) for label in labels)

    # Moods per day
    moods = Mood.query.filter(
        Mood.user_id == session["user_id"],
        Mood.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for m in moods:
        key = m.created_at.date().strftime("%Y-%m-%d")
        if key in moods_count:
            moods_count[key] += 1

    # Todos completed per day (by created_at)
    todos = ToDo.query.filter(
        ToDo.user_id == session["user_id"],
        ToDo.done.is_(True),
        ToDo.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for t in todos:
        key = t.created_at.date().strftime("%Y-%m-%d")
        if key in todos_done_count:
            todos_done_count[key] += 1

    # Habit completions per day
    habit_entries = HabitEntry.query.join(Habit).filter(
        Habit.user_id == session["user_id"],
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