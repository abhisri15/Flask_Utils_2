from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    current_user,
    logout_user,
    fresh_login_required
)
from urllib.parse import urlparse, urljoin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)

db = SQLAlchemy()
login_manager = LoginManager()
serializer = None

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(10))
    session_token = db.Column(db.String(100), unique=True)

    def get_id(self):
        return self.session_token

def create_user(serializer):
    user = User(
        username='Raj',
        password='abc',
        session_token=serializer.dumps(['Raj', 'abc'])
    )
    db.session.add(user)
    db.session.commit()

def update_token():
    Raj = User.query.filter_by(username='Raj').first()
    Raj.password = 'abcd'
    Raj.session_token = serializer.dumps(['Raj', 'abcd'])

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TIME_TO_EXPIRE'] = 3600

    db.init_app(app)
    login_manager.init_app(app)

    global serializer
    serializer = URLSafeTimedSerializer(app.secret_key)

    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.refresh_view = 'login'
    login_manager.needs_refresh_message = 'Session expired, please log in again.'

    @login_manager.user_loader
    def load_user(session_token):

        user = User.query.filter_by(session_token=session_token).first()

        try:
            serializer.loads(session_token, max_age=app.config['TIME_TO_EXPIRE'])

        except SignatureExpired:
            user.session_token = None
            db.session.commit()
            return None

        return user

    @app.route('/')
    def index():
        user = User.query.filter_by(username='Raj').first()

        session_token = serializer.dumps(['Raj', 'abc'])
        user.session_token = session_token
        db.session.commit()

        login_user(user, remember=True)
        return 'Welcome to the Flask Login! Home Page!'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user, remember=remember_me)

                if 'next' in session and session['next']:
                    if is_safe_url(session['next']):
                        return redirect(session['next'])

                return redirect(url_for('index'))

        session['next'] = request.args.get('next')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return 'Logged out successfully'

    @app.route('/profile')
    @login_required
    def profile():
        return f'User Profile: {current_user.username}'

    @app.route('/change')
    @fresh_login_required
    def change():
        return 'This is for fresh login only!'

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='Raj').first():
            create_user(serializer)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
