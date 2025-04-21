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
from pymongo.mongo_client import MongoClient
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = 'mongodb+srv://<db_username>:<db_password>@cluster0.4m87f.mongodb.net/test?retryWrites=true&w=majority'

mongo = PyMongo(app)
login_manager = LoginManager(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# UserMixin is a class provided by Flask-Login that provides default implementations for the methods required by Flask-Login
class Member(UserMixin):

    def __init__(self, member_data):
        self.member_data = member_data
    def get_id(self):
        return self.member_data['session_token']

@login_manager.user_loader
def load_user(user_id):
    members = mongo.db.members
    member_data = members.find_one({'session_token': user_id})
    if member_data:
        return Member(member_data)
    return None

@app.route('/create')
def create():
    members = mongo.db.members
    session_token = serializer.dumps(['Raj', 'abc'])
    members.insert_one({
        'username': 'Raj',
        'password': 'abc',
        'session_token': session_token
    })
    return 'User created!'

@app.route('/login')
def index():
    members = mongo.db.members
    member = members.find_one({'username': 'Raj'})
    Raj = Member(member)

    login_user(Raj)

    return 'User logged in!'

@app.route('/home')
@login_required
def home():
    return 'The current user is {}!'.format(current_user.member_data['username'])

@app.route('/logout')
@login_required
def logout():
    members = mongo.db.members
    member = members.find_one({'username': 'Raj'})
    Raj = Member(member)
    logout_user(Raj)
    return 'User logged out!'

print("Connected to MongoDB:", mongo.db)