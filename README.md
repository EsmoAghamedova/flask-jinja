
# CalmSpace 🌿
*A calm productivity & wellness tracker built with Flask*

![Flask](https://img.shields.io/badge/Flask-Backend-black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

CalmSpace is a cozy, minimal web app focused on mental wellness and productivity.  
Track moods, habits, and tasks, earn badges, and explore wellness tips — all in one calm space.

---

## ✨ Features
- 🧠 Mood tracking with notes
- ✅ To-do list with completion state
- 🔁 Habit tracker with checklists
- 💡 Tips system stored in database
- 🏅 Achievement badges & progress rewards
- 📊 Admin statistics dashboard
- 🛡️ Admin controls (ban/delete users, manage tips)
- 🔐 Secure authentication (hashed passwords + Flask-Login)

---

## 📊 App Statistics (Admin)
Admins can view:
- 👥 Total registered users
- 😊 Total moods logged
- ✅ Completed tasks count
- 🔥 Habit check-ins
- 💡 Total tips in database

Stats are calculated live from the database.

---

## 🏅 Badges System
Users can unlock badges such as:
- 🌱 First Mood Logged
- ✅ First Task Completed
- 🔥 7-Day Habit Streak
- 🧠 Consistency Master

Badges are awarded automatically based on activity.

---

## 🚀 Getting Started
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open in browser:
http://127.0.0.1:4000

---

## 🔐 Admin Access
An admin account is created on first run:

- Email: admin@calmspace.test
- Password: admin1234

You can override via environment variables:
```bash
export ADMIN_EMAIL="you@example.com"
export ADMIN_PASSWORD="supersecret"
```

---

## 🧭 Pages
- `/` — Home
- `/tracker` — Mood / Habit / To-do
- `/tips` — Tips library
- `/badges` — User achievements
- `/admin` — Admin dashboard

---

## 🗂️ Project Structure
```
app.py          # App setup & seeding
routes.py       # Blueprints & logic
models.py       # Database models
forms.py        # WTForms
templates/      # Jinja templates
static/         # CSS & assets
```

---

## 🎨 UI Style
- Calm green color palette
- Glassmorphism cards
- Minimal, distraction-free layout

---

## 📜 License
🪪 Licensed under the MIT License
