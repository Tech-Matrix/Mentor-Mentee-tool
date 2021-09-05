from datetime import datetime
from project import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    urole = db.Column(db.String(80))
    mentor = db.relationship('Mentor', backref='user', uselist=False)
    mentee = db.relationship('Mentee', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)


class Mentee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

