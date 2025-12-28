from collections import OrderedDict
from datetime import date, datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.common.auth import get_current_user, login_required
from app.common.user_helpers import calculate_badges, get_badge_definitions, get_user_stats
from extensions import db
from forms import ActionForm, HabitTrackerForm, MoodForm, ToDoForm
from models import Habit, HabitEntry, Mood, ToDo

bp = Blueprint("user", __name__)


@bp.route("/tracker")
@login_required
def tracker():
    user = get_current_user()
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    mood_count = Mood.query.filter_by(user_id=user.id).count()
    todo_count = ToDo.query.filter_by(user_id=user.id).count()
    todo_done_count = ToDo.query.filter_by(user_id=user.id, done=True).count()
    habit_count = Habit.query.filter_by(user_id=user.id).count()
    badges = calculate_badges(user.id)

    return render_template(
        "user/tracker.html",
        summary={
            "moods": mood_count,
            "todos": todo_count,
            "todos_done": todo_done_count,
            "habits": habit_count,
        },
        badges=badges,
    )


@bp.route("/badges")
@login_required
def badges():
    user = get_current_user()
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
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
    return render_template("user/badges.html", badges=all_badges, stats=stats)


@bp.route("/mood", methods=["GET", "POST"])
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
            return redirect(url_for("user.mood"))
        flash("Please correct the errors in the form.", "danger")

    moods = (
        Mood.query.filter_by(user_id=user.id)
        .order_by(Mood.created_at.desc())
        .all()
    )
    return render_template("user/mood.html", mood_form=mood_form, moods=moods)


@bp.route("/mood/edit/<int:mood_id>", methods=["GET", "POST"])
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
            return redirect(url_for("user.mood"))
        flash("Please correct the errors in the form.", "danger")
    return render_template("user/mood_edit.html", mood_form=mood_form, mood=mood_obj)


@bp.route("/mood/delete/<int:mood_id>", methods=["POST"])
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
    return redirect(url_for("user.mood"))


@bp.route("/habit", methods=["GET", "POST"])
@login_required
def habit():
    user = get_current_user()
    habit_form = HabitTrackerForm()
    action_form = ActionForm()
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
            return redirect(url_for("user.habit"))
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

    start_date = today - timedelta(days=13)
    last_14_days = [start_date + timedelta(days=offset) for offset in range(14)]
    recent_entries = HabitEntry.query.join(Habit).filter(
        Habit.user_id == user.id,
        HabitEntry.date >= start_date,
    ).all()
    completion_map = {}
    for entry in recent_entries:
        completion_map.setdefault(entry.habit_id, []).append(entry.date)

    daily_habits = [habit for habit in habits if (habit.frequency or "").lower() == "daily"]
    weekly_habits = [habit for habit in habits if (habit.frequency or "").lower() == "weekly"]
    monthly_habits = [habit for habit in habits if (habit.frequency or "").lower() == "monthly"]
    other_habits = [
        habit
        for habit in habits
        if (habit.frequency or "").lower() not in {"daily", "weekly", "monthly"}
    ]

    return render_template(
        "user/habit.html",
        habit_form=habit_form,
        habits=habits,
        completed_today=completed_today,
        action_form=action_form,
        last_14_days=last_14_days,
        completion_map=completion_map,
        daily_habits=daily_habits,
        weekly_habits=weekly_habits,
        monthly_habits=monthly_habits,
        other_habits=other_habits,
    )


@bp.route("/habit/complete/<int:habit_id>", methods=["POST"])
@login_required
def habit_complete(habit_id):
    user = get_current_user()
    action_form = ActionForm()
    if not action_form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("user.habit"))
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
    return redirect(url_for("user.habit"))


@bp.route("/habit/edit/<int:habit_id>", methods=["GET", "POST"])
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
            return redirect(url_for("user.habit"))
        flash("Please correct the errors in the form.", "danger")
    return render_template("user/habit_edit.html", habit_form=habit_form, habit=habit_obj)


@bp.route("/habit/delete/<int:habit_id>", methods=["POST"])
@login_required
def habit_delete(habit_id):
    user = get_current_user()
    action_form = ActionForm()
    if not action_form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("user.habit"))
    habit_obj = Habit.query.get_or_404(habit_id)
    if habit_obj.user_id != user.id:
        flash("You are not authorized to delete that habit.", "danger")
        abort(403)
    db.session.delete(habit_obj)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("user.habit"))


@bp.route("/habits/stats")
@login_required
def habit_stats():
    user = get_current_user()
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = date(today.year, today.month, 1)

    habits = Habit.query.filter_by(user_id=user.id).order_by(Habit.created_at.desc()).all()
    entries = HabitEntry.query.join(Habit).filter(
        Habit.user_id == user.id,
        HabitEntry.date >= month_start,
    ).all()

    week_counts = {habit.id: 0 for habit in habits}
    month_counts = {habit.id: 0 for habit in habits}
    for entry in entries:
        month_counts[entry.habit_id] = month_counts.get(entry.habit_id, 0) + 1
        if entry.date >= week_start:
            week_counts[entry.habit_id] = week_counts.get(entry.habit_id, 0) + 1

    return render_template(
        "user/habit_stats.html",
        habits=habits,
        week_counts=week_counts,
        month_counts=month_counts,
        week_start=week_start,
        month_start=month_start,
    )


@bp.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    user = get_current_user()
    todo_form = ToDoForm()
    action_form = ActionForm()
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
            return redirect(url_for("user.todo"))
        flash("Please correct the errors in the form.", "danger")

    active_todos = (
        ToDo.query.filter_by(user_id=user.id, done=False)
        .order_by(ToDo.created_at.desc())
        .all()
    )
    completed_todos = (
        ToDo.query.filter_by(user_id=user.id, done=True)
        .order_by(ToDo.created_at.desc())
        .all()
    )
    return render_template(
        "user/todo.html",
        todo_form=todo_form,
        action_form=action_form,
        active_todos=active_todos,
        completed_todos=completed_todos,
    )


@bp.route("/todo/<int:todo_id>/toggle", methods=["POST"])
@login_required
def todo_toggle(todo_id):
    user = get_current_user()
    action_form = ActionForm()
    if not action_form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("user.todo"))
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != user.id:
        flash("You are not authorized to edit that task.", "danger")
        abort(403)
    todo_obj.done = not todo_obj.done
    db.session.commit()
    flash("Task updated.", "success")
    return redirect(url_for("user.todo"))


@bp.route("/todo/edit/<int:todo_id>", methods=["GET", "POST"])
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
            return redirect(url_for("user.todo"))
        flash("Please correct the errors in the form.", "danger")
    return render_template("user/todo_edit.html", todo_form=todo_form, todo=todo_obj)


@bp.route("/todo/delete/<int:todo_id>", methods=["POST"])
@login_required
def todo_delete(todo_id):
    user = get_current_user()
    action_form = ActionForm()
    if not action_form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("user.todo"))
    todo_obj = ToDo.query.get_or_404(todo_id)
    if todo_obj.user_id != user.id:
        flash("You are not authorized to delete that task.", "danger")
        abort(403)
    db.session.delete(todo_obj)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("user.todo"))


@bp.route("/progress")
@login_required
def progress():
    days = 14
    user = get_current_user()
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days - 1)
    labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    moods_count = OrderedDict((label, 0) for label in labels)
    todos_done_count = OrderedDict((label, 0) for label in labels)
    habits_done_count = OrderedDict((label, 0) for label in labels)

    moods = Mood.query.filter(
        Mood.user_id == user.id,
        Mood.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for mood_entry in moods:
        key = mood_entry.created_at.date().strftime("%Y-%m-%d")
        if key in moods_count:
            moods_count[key] += 1

    todos = ToDo.query.filter(
        ToDo.user_id == user.id,
        ToDo.done.is_(True),
        ToDo.created_at >= datetime.combine(start_date, datetime.min.time()),
    ).all()
    for todo_entry in todos:
        key = todo_entry.created_at.date().strftime("%Y-%m-%d")
        if key in todos_done_count:
            todos_done_count[key] += 1

    habit_entries = HabitEntry.query.join(Habit).filter(
        Habit.user_id == user.id,
        HabitEntry.date >= start_date,
    ).all()
    for entry in habit_entries:
        key = entry.date.strftime("%Y-%m-%d")
        if key in habits_done_count:
            habits_done_count[key] += 1

    return render_template(
        "user/progress.html",
        labels=labels,
        moods_data=list(moods_count.values()),
        todos_data=list(todos_done_count.values()),
        habits_data=list(habits_done_count.values()),
        days=days,
    )
