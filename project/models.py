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
    hobbies = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    lat = db.Column(db.Float, nullable=True)
    long = db.Column(db.Float, nullable=True)
    time_delta = db.Column(db.Float, nullable=True)
    gender = db.Column(db.String, nullable=True)
    language = db.Column(db.String, nullable=True)
    expertise_1 = db.Column(db.String, nullable=True)
    bq_1 = db.Column(db.String, nullable=True)
    bq_2 = db.Column(db.String, nullable=True)
    ready = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    mentees = db.relationship("Mentee", backref="mentor", lazy=True)


class Mentee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hobbies = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    lat = db.Column(db.Float, nullable=True)
    long = db.Column(db.Float, nullable=True)
    time_delta = db.Column(db.Float, nullable=True)
    gender_pref = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    language_pref = db.Column(db.String, nullable=True)
    aspiration = db.Column(db.String, nullable=True)
    bq_1 = db.Column(db.String, nullable=True)
    bq_2 = db.Column(db.String, nullable=True)
    ready = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'), unique=True, nullable=True)

    def connect(self, mentor):
        self.mentor = mentor
        db.session.commit()

    def disconnect(self):
        self.mentor = None
        db.session.commit()

# mentor = Mentor(hobbies="laughing", city="bangalore", gender="male", expertise_1="art", bq_1="good guy", ready=False, user_id=user.id)
