# CalmSpace 🌿
*A calm productivity & wellness tracker built with Flask.*

![Flask](https://img.shields.io/badge/Flask-Backend-black)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![SQLite](https://img.shields.io/badge/SQLite-Dev%20Database-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

CalmSpace is a cozy, minimal web app focused on mental wellness and productivity.  
Track moods, habits, and tasks, earn badges, and explore wellness tips — all in one calm space.

---

## ✨ Features
- 🧠 Mood tracking with notes
- ✅ To-do list with completion state
- 🔁 Habit tracker with check-ins
- 💡 Tips system stored in database
- 🏅 Achievement badges & progress rewards
- 📊 Admin statistics dashboard
- 🛡️ Admin controls (ban users, manage tips)
- 🔐 Secure authentication (hashed passwords)
- 📩 Email verification (Resend)
- 🔁 Password reset via email token (Resend)

---

## 🧠 How Auth Works
**Email Verification**
- User signs up → receives a verification link (token with purpose=`verify`, expires)
- Clicking the link sets `email_verified=True`

**Password Reset**
- User requests reset → receives a reset link (token with purpose=`reset`, expires)
- GET `/reset-password` validates token + shows form
- POST `/reset-password` validates again + updates password (and marks token used)

---

## 📊 Admin Statistics
Admins can view live stats such as:
- 👥 Total registered users
- 😊 Total moods logged
- ✅ Completed tasks count
- 🔥 Habit check-ins
- 💡 Total tips in database

---

## 🏅 Badges System
Users can unlock badges such as:
- 🌱 First Mood Logged
- ✅ First Task Completed
- 🔥 7-Day Habit Streak
- 🧠 Consistency Master

---

## 🧭 Main Pages
- `/` — Home
- `/auth/signup` — Sign up
- `/auth/login` — Log in
- `/auth/resend` — Resend verification email
- `/auth/forgot-password` — Request password reset
- `/auth/reset-password` — Reset password (token link)
- `/tracker` — Mood / Habit / To-do
- `/tips` — Tips library
- `/badges` — User achievements
- `/admin` — Admin dashboard

---

## 🗂️ Project Structure (example)
```
app.py
app/
  __init__.py
  wsgi.py
  extensions.py
  models/
  routes/
  forms/
  utils/
  templates/
  static/
```

---

## 🚀 Getting Started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open in browser:
http://127.0.0.1:4000

---

## 🔐 Admin Access
- Email: 
- Password: 

(i will add it...i have admin acces but with my personal email and i dont want share it :) )
---

## 🎨 UI Style
- Calm green color palette
- Glassmorphism cards
- Minimal, distraction-free layout

---

## 📜 License
MIT License
