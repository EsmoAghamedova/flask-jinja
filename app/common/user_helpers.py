from models import Habit, HabitEntry, Mood, ToDo


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


def reset_user_progress(db, user, category):
    if category == "moods" or category == "all":
        Mood.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    if category == "todos" or category == "all":
        ToDo.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    if category == "habits" or category == "all":
        habit_ids = [habit.id for habit in Habit.query.filter_by(user_id=user.id).all()]
        if habit_ids:
            HabitEntry.query.filter(HabitEntry.habit_id.in_(habit_ids)).delete(
                synchronize_session=False
            )
        Habit.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.flush()


def delete_user_account(db, user):
    db.session.delete(user)
    db.session.flush()
