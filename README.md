# CalmSpace 🌿✨

A calm, friendly productivity and wellness tracker built with Flask + Jinja. Track moods, habits, and to-dos, discover tips, and celebrate progress with motivational badges.

---

## 📊 Project Stats (live from the app)
- 👥 **Users**: _tracked in DB_
- 😊 **Moods logged**: _tracked in DB_
- ✅ **Tasks completed**: _tracked in DB_
- 🔥 **Habit check-ins**: _tracked in DB_
- 💡 **Tips**: _managed by admin_

> These stats are shown in the **Admin Dashboard** once the app is running.

---

## ✨ Features
- 🧠 **Mood Tracker** — log moods with notes
- ✅ **To-Do List** — add, edit, complete tasks
- 🔁 **Habit Tracker** — build daily routines
- 💡 **Tips Library** — admin-managed tips in DB
- 🏅 **Badges** — unlock motivational achievements + confetti
- ❄️ **Snowflakes** — ambient site-wide effect
- 🛡️ **Admin Panel** — stats dashboard + user roles + tip CRUD

---

## 🚀 Quick Start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:4000

---

## 🔐 Admin Access
The app seeds an admin user on first run:
- **Email**: `admin@calmspace.test`
- **Password**: `admin1234`

You can also configure via env:
```bash
export ADMIN_EMAIL="you@example.com"
export ADMIN_PASSWORD="supersecret"
```

---

## 🧭 Main Pages
- `/` — Home
- `/tracker` — Tracker dashboard (user)
- `/badges` — Badges & unlocks (user)
- `/tips` — Public tips list (user)
- `/admin` — Admin dashboard

---

## 🗂️ Project Structure
```
app.py            # app boot + seed + schema helpers
routes.py         # routes + logic
models.py         # SQLAlchemy models
forms.py          # WTForms
templates/        # Jinja templates
static/style/     # CSS styles
```

---

## 🧪 Testing
```bash
python -m compileall .
```

---

## 📸 UI Highlights
- Glassmorphism cards
- Badge celebrations
- Calm green palette

---

## 📜 License
MIT
