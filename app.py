import os

from flask import Flask
from sqlalchemy import inspect, text

from extensions import db
from models import Tip, User
from routes import main

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(main)
print("URL map:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)


def ensure_schema():
    inspector = inspect(db.engine)
    user_columns = {col["name"] for col in inspector.get_columns("users")} if inspector.has_table("users") else set()

    if "is_admin" not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
    if "created_at" not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))

    if not inspector.has_table("tips"):
        Tip.__table__.create(db.engine)

    db.session.commit()


def ensure_seed_data():
    admins_to_seed = [
        {
            "username": "admin",
            "email": os.getenv("ADMIN_EMAIL", "admin@calmspace.test"),
            "password": os.getenv("ADMIN_PASSWORD", "admin1234"),
        },
        {
            "username": "esmira",
            "email": "esmira.agamedovate03@geolab.edu.ge",
            "password": "EsmoAdmin2009<3",
        },
    ]

    for admin in admins_to_seed:
        admin_user = User.query.filter_by(email=admin["email"]).first()
        if not admin_user:
            admin_user = User(
                username=admin["username"],
                email=admin["email"],
                is_admin=True,
            )
            admin_user.set_password(admin["password"])
            db.session.add(admin_user)
            db.session.commit()

    if Tip.query.count() == 0:
        starter_tips = [
            Tip(title="🧘‍♀️ Meditation", body="Spend 5–10 minutes focusing on your breath.", category="Mindfulness", author=admin_user),
            Tip(title="💧 Hydration", body="Drink a glass of water as soon as you wake up.", category="Energy", author=admin_user),
            Tip(title="📓 Journaling", body="Write down one win and one lesson from today.", category="Reflection", author=admin_user),
        ]
        db.session.bulk_save_objects(starter_tips)
        db.session.commit()


with app.app_context():
    vf = app.view_functions

    def _add_alias(rule, endpoint, blueprint_view_name, methods=None):
        view = vf.get(blueprint_view_name)
        if view and endpoint not in vf:
            if methods:
                app.add_url_rule(rule, endpoint=endpoint, view_func=view, methods=methods)
            else:
                app.add_url_rule(rule, endpoint=endpoint, view_func=view)

    _add_alias('/', 'home', 'main.home')
    _add_alias('/tracker', 'tracker', 'main.tracker')
    _add_alias('/mood', 'mood', 'main.mood', methods=['GET', 'POST'])
    _add_alias('/habit', 'habit', 'main.habit', methods=['GET', 'POST'])
    _add_alias('/todo', 'todo', 'main.todo', methods=['GET', 'POST'])
    _add_alias('/tips', 'tips', 'main.tips')
    _add_alias('/tip/<int:tip_id>', 'tip', 'main.tip_detail')
    _add_alias('/badges', 'badges', 'main.badges')
    _add_alias('/signup', 'signup', 'main.signup', methods=['GET', 'POST'])
    _add_alias('/login', 'login', 'main.login', methods=['GET', 'POST'])

    db.create_all()
    ensure_schema()
    ensure_seed_data()

if __name__ == "__main__":
    app.run(debug=True, port=4000)
