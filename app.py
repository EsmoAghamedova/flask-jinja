from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime
from forms import MoodForm, ToDoForm, HabitTrackerForm
app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890'

users = [
    {"username": "Gvantsa", "email": "gvantsa.euashvili@gmail.com", "password": "Gvantsa321"},
    {"username": "Esmo", "email": "esmo.agamedova@gmail.com", "password": "Esmo123"},
    {"username": "Nini", "email": "nini.iakobidze@gmail.com", "password": "Nini456"},
    {"username": "Tedo", "email": "tedo.ratiani@gmail.com", "password": "tedo789"},
    {"username": "Zuka", "email": "zuka.abashidze@gmail.com", "password": "Zuka101"}
]

tips_list = [
    {"title": "🧘‍♀️ Meditation", "text": "Spend 5–10 minutes focusing on your breath to reduce stress."},
    {"title": "🌿 Nature Walks", "text": "Take a walk outside to clear your mind and boost creativity."},
    {"title": "📓 Journaling", "text": "Write down your thoughts and gratitude to reflect and relax."},
    {"title": "💧 Hydration", "text": "Drink enough water daily to keep your body and mind fresh."},
    {"title": "🛌 Sleep Routine", "text": "Go to bed and wake up at consistent times to feel energized."},
    {"title": "🎵 Music Breaks", "text": "Listen to calming music to recharge and stay focused."}
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

moods_list = []

@app.route('/mood', methods=['GET', 'POST'])
def mood():
    form = MoodForm()
    if form.validate_on_submit():
        moods_list.append({
            "mood": form.mood.data,
            "notes": form.notes.data,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        return redirect(url_for('mood'))
    return render_template('mood.html', form=form, moods=moods_list)

habits_list = []

@app.route('/habit', methods=['GET', 'POST'])
def habit():
    form = HabitTrackerForm()
    if form.validate_on_submit():
        habits_list.append({
            "habit": form.habit.data,
            "frequency": form.frequency.data,
            "done": False
        })
        return redirect(url_for('habit'))
    return render_template('habit.html', form=form, habits=habits_list)

todos_list = []

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    form = ToDoForm()
    if form.validate_on_submit():
        todos_list.append({
            "task": form.task.data,
            "detail": form.detail.data,
            "done": False
        })
        return redirect(url_for('todo'))
    return render_template('todo.html', form=form, todos=todos_list)

@app.route('/tips')
def tips():
    return render_template("tips.html", tips=tips_list)

@app.route('/tip/<int:tip_id>')
def tip_detail(tip_id):
    tip = tips_list[tip_id]
    return render_template("tip.html", tip=tip)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        for user in users:
            if user['email'] == email and user['password'] == password:
                return redirect(url_for('home'))
        error = 'Invalid email or password. Please try again.'
    return render_template('login.html', error=error)


if __name__ == "__main__":
    app.run(debug=True, port=4000)
