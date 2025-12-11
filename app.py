from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

users = [
    {"username": "Gvantsa", "email" : "gvantsa.euashvili@gmail.com" , "password": "Gvantsa321"},
    {"username": "Esmo", "email" : "esmo.agamedova@gmail.com" , "password": "Esmo123"},
    {"username": "Nini", "email" : "nini.iakobidze@gmail.com" , "password": "Nini456"},
    {"username": "Tedo", "email" : "tedo.ratiani@gmail.com" , "password": "tedo789"},
    {"username": "Zuka", "email" : "zuka.abashidze@gmail.com" , "password": "Zuka101"}
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

@app.route('/tips')
def tips():
    tips_list = [
        {"title": "🧘‍♀️ Meditation", "text": "Spend 5–10 minutes focusing on your breath to reduce stress."},
        {"title": "🌿 Nature Walks", "text": "Take a walk outside to clear your mind and boost creativity."},
        {"title": "📓 Journaling", "text": "Write down your thoughts and gratitude to reflect and relax."},
        {"title": "💧 Hydration", "text": "Drink enough water daily to keep your body and mind fresh."},
        {"title": "🛌 Sleep Routine", "text": "Go to bed and wake up at consistent times to feel energized."},
        {"title": "🎵 Music Breaks", "text": "Listen to calming music to recharge and stay focused."}
    ]

    return render_template("tips.html", tips=tips_list)

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


app.run(debug=True, port=4000)