from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, login_required, current_user
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_APP_NAME'] = "Flask-User App"
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('mail_config.cfg')

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, default=True, server_default='0')
    email = db.Column(db.String(150), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

@app.route('/')
def index():
    return "This is the unprotected index page."

@app.route('/profile')
@login_required
def profile():
    return "Hello, {}".format(current_user.username)

if __name__ == '__main__':
    app.run(debug=True)