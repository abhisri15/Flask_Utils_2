from flask import Flask, request, redirect, url_for
from flask_admin import Admin, BaseView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.fileadmin import FileAdmin
from os.path import join, dirname
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_db.db'
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)
admin = Admin(app, template_mode='bootstrap4')
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    birthday = db.Column(db.DateTime)

    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.username)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Comment %r>' % (self.id)


class UserView(ModelView):
    column_exclude_list = ['']
    column_display_pk = True  # Display primary key
    can_edit = True
    can_create = True
    can_delete = False
    can_export = True

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = generate_password_hash(model.password, method='sha256')
        else:
            model.password = form.password.data

    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return 'You are not allowed to access this page.'
class CommentView(ModelView):
    create_modal = True

class NotificationView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notification.html')

admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Comment, db.session))

path = join(dirname(__file__), 'uploads')
admin.add_view(FileAdmin(path, '/uploads/', name='Uploads'))

admin.add_view(NotificationView(name='Notifications', endpoint='notify'))

@app.route('/login')
def login():
    user = User.query.filter_by(id=1).first()
    login_user(user)
    return redirect(url_for('admin.index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.index'))

if __name__ == "__main__":
    app.run(debug=True)