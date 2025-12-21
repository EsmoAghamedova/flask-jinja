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

# მას აქ რატომღაც სულ ერორს მიჩჩვენებდა და რამე და ამიტომაც AI-ით გამოვასწორე 😅

app.register_blueprint(main)
print("URL map:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)

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
    _add_alias('/signup', 'signup', 'main.signup', methods=['GET', 'POST'])
    _add_alias('/login', 'login', 'main.login', methods=['GET', 'POST'])

    # create DB tables (unchanged)
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=4000)