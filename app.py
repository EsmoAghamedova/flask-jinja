# import os

# from flask import Flask
# from sqlalchemy import inspect, text

# from app.common.auth import register_auth_handlers
# from app.routes import admin, auth, public, settings, user
# from extensions import db
# from models import Tip, User

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

# basedir = os.path.abspath(os.path.dirname(__file__))

# db_url = os.getenv("DATABASE_URL")

# if db_url:
#     db_url = db_url.replace("postgres://", "postgresql://", 1)

#     if db_url.startswith("postgresql://"):
#         db_url = "postgresql+psycopg://" + db_url[len("postgresql://"):]

#     app.config["SQLALCHEMY_DATABASE_URI"] = db_url

#     app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#         "connect_args": {"sslmode": "require"}
#     }
#     USING_POSTGRES = True
# else:
#     instance_dir = os.path.join(basedir, "instance")
#     os.makedirs(instance_dir, exist_ok=True)

#     app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(instance_dir, "app.db")
#     USING_POSTGRES = False

# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db.init_app(app)
# print("USING DATABASE:", app.config["SQLALCHEMY_DATABASE_URI"])

# register_auth_handlers(app)
# app.register_blueprint(public.bp)
# app.register_blueprint(auth.bp)
# app.register_blueprint(user.bp)
# app.register_blueprint(settings.bp)
# app.register_blueprint(admin.bp)
# print("URL map:")
# for rule in app.url_map.iter_rules():
#     print(rule.endpoint, "->", rule)


# from sqlalchemy import inspect, text

# def ensure_schema():
#     inspector = inspect(db.engine)
#     user_columns = (
#         {col["name"] for col in inspector.get_columns("users")}
#         if inspector.has_table("users")
#         else set()
#     )

#     if "email_verified" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE")
#         )

#     if "email_verified_at" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMPTZ")
#         )

#     if "is_admin" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE")
#         )

#     if "is_banned" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE")
#         )

#     if "created_at" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ")
#         )

#     if "password_reset_jti" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN password_reset_jti VARCHAR(100)")
#         )

#     if "password_reset_used_at" not in user_columns:
#         db.session.execute(
#             text("ALTER TABLE users ADD COLUMN password_reset_used_at TIMESTAMPTZ")
#         )

#     if not inspector.has_table("chat_sessions"):
#         db.session.execute(
#             text("""
#             CREATE TABLE chat_sessions (
#                 id SERIAL PRIMARY KEY,
#                 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#                 is_active BOOLEAN NOT NULL DEFAULT TRUE,
#                 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
#             )
#             """)
#         )

#     if not inspector.has_table("chat_messages"):
#         db.session.execute(
#             text("""
#             CREATE TABLE chat_messages (
#                 id SERIAL PRIMARY KEY,
#                 session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
#                 role VARCHAR(20) NOT NULL,
#                 content TEXT NOT NULL,
#                 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
#             )
#             """)
#         )

#     db.session.commit()

#     if not inspector.has_table("tips"):
#         Tip.__table__.create(db.engine)


#     db.session.commit()


# def ensure_seed_data():
#     admins_to_seed = [
#         {
#             "username": "admin",
#             "email": os.getenv("ADMIN_EMAIL", "admin@calmspace.test"),
#             "password": os.getenv("ADMIN_PASSWORD", "admin1234"),
#         }
#     ]

#     for admin in admins_to_seed:
#         admin_user = User.query.filter_by(email=admin["email"]).first()
#         if not admin_user:
#             admin_user = User(
#                 username=admin["username"],
#                 email=admin["email"],
#                 is_admin=True,
#             )
#             admin_user.set_password(admin["password"])
#             db.session.add(admin_user)
#             db.session.commit()

#     if Tip.query.count() == 0:
#         starter_tips = [
#             Tip(title="🧘‍♀️ Meditation", body="Spend 5–10 minutes focusing on your breath.", category="Mindfulness", author=admin_user),
#             Tip(title="💧 Hydration", body="Drink a glass of water as soon as you wake up.", category="Energy", author=admin_user),
#             Tip(title="📓 Journaling", body="Write down one win and one lesson from today.", category="Reflection", author=admin_user),
#         ]
#         db.session.bulk_save_objects(starter_tips)
#         db.session.commit()


# with app.app_context():
#     vf = app.view_functions

#     def _add_alias(rule, endpoint, blueprint_view_name, methods=None):
#         view = vf.get(blueprint_view_name)
#         if view and endpoint not in vf:
#             if methods:
#                 app.add_url_rule(rule, endpoint=endpoint, view_func=view, methods=methods)
#             else:
#                 app.add_url_rule(rule, endpoint=endpoint, view_func=view)

#     _add_alias('/', 'home', 'public.home')
#     _add_alias('/dashboard', 'dashboard', 'user.dashboard')
#     _add_alias('/tracker', 'tracker', 'user.tracker')
#     _add_alias('/mood', 'mood', 'user.mood', methods=['GET', 'POST'])
#     _add_alias('/habit', 'habit', 'user.habit', methods=['GET', 'POST'])
#     _add_alias('/todo', 'todo', 'user.todo', methods=['GET', 'POST'])
#     _add_alias('/tips', 'tips', 'public.tips')
#     _add_alias('/tip/<int:tip_id>', 'tip', 'public.tip_detail')
#     _add_alias('/badges', 'badges', 'user.badges')
#     _add_alias('/signup', 'signup', 'auth.signup', methods=['GET', 'POST'])
#     _add_alias('/login', 'login', 'auth.login', methods=['GET', 'POST'])
#     _add_alias('/logout', 'logout', 'auth.logout')

#     db.create_all()
#     ensure_schema()
#     ensure_seed_data()

# if __name__ == "__main__":
#     app.run(debug=True, port=4000)


import os
from flask import Flask
from sqlalchemy import inspect, text
from app.common.auth import register_auth_handlers
from app.routes import admin, auth, public, settings, user
from extensions import db
from models import Tip, User

# --- Flask app setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

basedir = os.path.abspath(os.path.dirname(__file__))

# --- Database config ---
db_url = os.getenv("DATABASE_URL")
if db_url:
    db_url = db_url.replace("postgres://", "postgresql://", 1)
    if db_url.startswith("postgresql://"):
        db_url = "postgresql+psycopg://" + db_url[len("postgresql://"):]
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"sslmode": "require"}}
    USING_POSTGRES = True
else:
    instance_dir = os.path.join(basedir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
        os.path.join(instance_dir, "app.db")
    USING_POSTGRES = False

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

print("USING DATABASE:", app.config["SQLALCHEMY_DATABASE_URI"])

# --- Register auth & blueprints ---
register_auth_handlers(app)
app.register_blueprint(public.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(settings.bp)
app.register_blueprint(admin.bp)

print("URL map:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)

# --- Seed data function ---


def ensure_seed_data():
    """Seed admin user and starter tips."""
    with app.app_context():
        admin_email = os.getenv("ADMIN_EMAIL", "admin@calmspace.test")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin1234")

        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(username="admin",
                              email=admin_email, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()

        if Tip.query.count() == 0:
            starter_tips = [
                Tip(title="🧘‍♀️ Meditation",
                    body="Spend 5–10 minutes focusing on your breath.",
                    category="Mindfulness", author=admin_user),
                Tip(title="💧 Hydration",
                    body="Drink a glass of water as soon as you wake up.",
                    category="Energy", author=admin_user),
                Tip(title="📓 Journaling",
                    body="Write down one win and one lesson from today.",
                    category="Reflection", author=admin_user),
            ]
            db.session.bulk_save_objects(starter_tips)
            db.session.commit()


# --- Route aliases ---
with app.app_context():
    vf = app.view_functions

    def _add_alias(rule, endpoint, blueprint_view_name, methods=None):
        view = vf.get(blueprint_view_name)
        if view and endpoint not in vf:
            if methods:
                app.add_url_rule(rule, endpoint=endpoint,
                                 view_func=view, methods=methods)
            else:
                app.add_url_rule(rule, endpoint=endpoint, view_func=view)

    _add_alias('/', 'home', 'public.home')
    _add_alias('/dashboard', 'dashboard', 'user.dashboard')
    _add_alias('/tracker', 'tracker', 'user.tracker')
    _add_alias('/mood', 'mood', 'user.mood', methods=['GET', 'POST'])
    _add_alias('/habit', 'habit', 'user.habit', methods=['GET', 'POST'])
    _add_alias('/todo', 'todo', 'user.todo', methods=['GET', 'POST'])
    _add_alias('/tips', 'tips', 'public.tips')
    _add_alias('/tip/<int:tip_id>', 'tip', 'public.tip_detail')
    _add_alias('/badges', 'badges', 'user.badges')
    _add_alias('/signup', 'signup', 'auth.signup', methods=['GET', 'POST'])
    _add_alias('/login', 'login', 'auth.login', methods=['GET', 'POST'])
    _add_alias('/logout', 'logout', 'auth.logout')

# --- DB setup (tables + schema + seed data) ---
with app.app_context():
    try:
        db.create_all()  # create all model tables

        # --- safe schema updates (Postgres friendly) ---
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN NOT NULL DEFAULT FALSE")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_jti VARCHAR(100)")
        db.session.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_used_at TIMESTAMPTZ")

        db.session.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """)
        db.session.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """)
        db.session.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            body TEXT,
            category VARCHAR(100),
            author_id INTEGER REFERENCES users(id)
        )
        """)

        db.session.commit()

        # seed admin + starter tips
        ensure_seed_data()

    except Exception as e:
        print("DB setup error:", e)
        db.session.rollback()

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True, port=4000)
