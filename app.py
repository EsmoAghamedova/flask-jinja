from flask import Flask
from extensions import db
from routes import main
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# register the blueprint as before
app.register_blueprint(main)
# after app.register_blueprint(main)
print("URL map:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)

# ---------------------------------------------------------------------
# Create top-level alias endpoints so calls like url_for('home') work.
# This maps the blueprint view functions (e.g. 'main.home') to simple
# endpoints (e.g. 'home'). Callers that expect 'home' (no blueprint
# prefix) will stop raising BuildError.
#
# NOTE: This is a compatibility helper. The long-term clean solution is
# to update templates/code to use the blueprint-aware endpoints:
#   - inside blueprint templates use {{ url_for('.home') }}
#   - across the app use url_for('main.home')
# ---------------------------------------------------------------------
with app.app_context():
    # Only add aliases when the blueprint view functions exist
    vf = app.view_functions

    def _add_alias(rule, endpoint, blueprint_view_name, methods=None):
        view = vf.get(blueprint_view_name)
        # if the blueprint view exists and the alias endpoint doesn't yet exist, add it
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
    _add_alias('/signup', 'signup', 'main.signup', methods=['GET', 'POST'])
    _add_alias('/login', 'login', 'main.login', methods=['GET', 'POST'])

    # create DB tables (unchanged)
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=4000)