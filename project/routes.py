import os
from functools import wraps
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from project import app, db, bcrypt, mail
from project.forms import RegistrationForm, LoginForm, ContactForm, MenteeForm, MentorForm, ConnectForm,DisconnectForm, FindForm
from project.models import User, Mentor, Mentee
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime
import pytz

import pandas as pd
from ML_model2 import model


tf = TimezoneFinder()
geolocator = Nominatim(user_agent='myapplication')

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
                return app.login_manager.unauthorized()
            urole = current_user.urole # app.login_manager.reload_user().get_urole()
            if (urole != role) and (role != "ANY"):
                return app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route("/")
@app.route("/home")
def home():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(form.subject.data, sender="prajwalguptacr@yahoo.com", recipients=["prajwalguptacr@yahoo.com"])
        msg.body = """
              From: %s <%s>
              %s
              """ % (form.name.data, form.email.data, form.message.data)
        mail.send(msg)
        return redirect(url_for("home"))
    return render_template('index.html', form=form)


@app.route("/login")
def login():
    return render_template('index.html')


@app.route("/login-mentor", methods=['GET', 'POST'])
def login_mentor():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginmentor.html', form=form)


@app.route("/login-mentee", methods=['GET', 'POST'])
def login_mentee():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginmentee.html', form=form)


@app.route("/register")
def register():
    return render_template('index.html')


@app.route("/register-mentor", methods=['GET', 'POST'])
def register_mentor():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data, email=form.email.data,
                    phone=form.phone.data, password=hashed_password, urole="MENTOR")
        user.mentor = Mentor()
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account has been created! You are now logged in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    my_var = "Everyone"
    return render_template('signupmentor.html', form=form, my_var="Everyone")


@app.route("/register-mentee", methods=['GET', 'POST'])
def register_mentee():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data, email=form.email.data,
                    phone=form.phone.data, password=hashed_password, urole="MENTEE")
        user.mentee = Mentee()
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account has been created! You are now logged in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('signupmentee.html', form=form)


@app.route("/profile", methods=['GET', 'POST'])
@login_required(role="ANY")
def profile():
    print(User.query.get(1))
    ready = False
    pot_mentors = []
    connect_form = ConnectForm()
    disconnect_form = DisconnectForm()
    find_form = FindForm()
    form = MentorForm()
    form2 = MenteeForm()
    print(current_user.urole)
    if current_user.urole == "MENTEE":
        print("Inside mentee")
        mentee = current_user.mentee
        ready = current_user.mentee.ready
        if request.method == 'GET':
            form2.fullname.data = current_user.fullname
            form2.username.data = current_user.username
            form2.email.data = current_user.email
            form2.phone.data = current_user.phone
            form2.city.data = mentee.city
            form2.gender.data = mentee.gender
            form2.gender_pref.data = mentee.gender_pref
            form2.language_pref.data = mentee.language_pref
            form2.aspiration.data = mentee.aspiration
            form2.b1.data = mentee.bq_1
            form2.b2.data = mentee.bq_2
            form2.hobbies.data = mentee.hobbies
        else:
            if form2.validate_on_submit() and form2.submit2.data:
                current_user.fullname = form2.fullname.data
                current_user.username = form2.username.data
                current_user.email = form2.email.data
                current_user.phone = form2.phone.data
                current_user.mentee.city = form2.city.data
                current_user.mentee.gender = form2.gender.data
                current_user.mentee.gender_pref = form2.gender_pref.data
                current_user.mentee.language_pref = form2.language_pref.data
                current_user.mentee.aspiration = form2.aspiration.data
                current_user.mentee.bq_1 = form2.b1.data
                current_user.mentee.bq_2 = form2.b2.data
                current_user.mentee.hobbies = form2.hobbies.data

                location = geolocator.geocode(form2.city.data)
                t_zone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
                pacific_now = datetime.datetime.now(pytz.timezone(t_zone))
                offset = pacific_now.utcoffset().total_seconds() / 60 / 60
                current_user.mentee.lat = location.latitude
                current_user.mentee.long = location.longitude
                current_user.mentee.time_delta = offset

                if(
                    current_user.mentee.city and
                    current_user.mentee.gender and
                    current_user.mentee.gender_pref and
                    current_user.mentee.language_pref and
                    current_user.mentee.aspiration and
                    current_user.mentee.bq_1 and
                    current_user.mentee.bq_2 and
                    current_user.mentee.hobbies and
                    current_user.mentee.lat and
                    current_user.mentee.long and
                    current_user.mentee.time_delta
                ):
                    current_user.mentee.ready = True
                    ready = True

                db.session.commit()
                flash('Your account has been updated!', 'success')
                return redirect(url_for('profile'))

            if connect_form.validate_on_submit() and connect_form.connect.data:
                mentor_to_connect_id = request.form.get('mentor_to_connect')
                mentor_to_connct = Mentor.query.filter_by(id=mentor_to_connect_id).first()
                if mentor_to_connct:
                    mentee.connect(mentor_to_connct)
                    # flash
                    return redirect(url_for('profile'))
                else:
                    # flash
                    return redirect(url_for('profile'))

            if disconnect_form.validate_on_submit() and disconnect_form.disconnect.data:
                mentee.disconnect()
                # flash
                return redirect(url_for('profile'))

            if find_form.validate_on_submit() and find_form.find.data:
                df = model()
                print(df)
                print("User ID:", current_user.id)
                assigned_cluster = df.iloc[current_user.id-1, -1]
                print("Assigned cluster:", assigned_cluster)
                df["id"] = [i for i in range(1, df.shape[0] + 1)]
                df = df.loc[df["Cluster #"]==assigned_cluster]
                for ind in df.index:
                    print(df["id"][ind])
                    id = df["id"][ind]
                    pot_user = User.query.all()[id-1]
                    if pot_user and pot_user.urole == "MENTOR" and pot_user.mentor.gender == mentee.gender_pref and pot_user.mentor.language == mentee.language_pref:
                        pot_mentors.append(pot_user.mentor)
                        return redirect(url_for('profile'))

    elif current_user.urole == "MENTOR":
        mentor = current_user.mentor
        ready = current_user.mentor.ready

        if request.method == 'GET':

            form.fullname.data = current_user.fullname
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.phone.data = current_user.phone
            form.city.data = mentor.city
            form.gender.data = mentor.gender
            form.language.data = mentor.language
            form.expertise.data = mentor.expertise_1
            form.b1.data = mentor.bq_1
            form.b2.data = mentor.bq_2
            form.hobbies.data = mentor.hobbies

        else:
            if form.validate_on_submit() and form.submit.data:
                current_user.fullname = form.fullname.data
                current_user.username = form.username.data
                current_user.email = form.email.data
                current_user.phone = form.phone.data
                current_user.mentor.city = form.city.data
                current_user.mentor.gender = form.gender.data
                current_user.mentor.language = form.language.data
                current_user.mentor.expertise_1 = form.expertise.data
                current_user.mentor.bq_1 = form.b1.data
                current_user.mentor.bq_2 = form.b2.data
                current_user.mentor.hobbies = form.hobbies.data

                location = geolocator.geocode(form.city.data)
                t_zone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
                pacific_now = datetime.datetime.now(pytz.timezone(t_zone))
                offset = pacific_now.utcoffset().total_seconds() / 60 / 60
                current_user.mentor.lat = location.latitude
                current_user.mentor.long = location.longitude
                current_user.mentor.time_delta = offset

                if (
                        current_user.mentor.city and
                        current_user.mentor.gender and
                        current_user.mentor.language and
                        current_user.mentor.expertise_1 and
                        current_user.mentor.bq_1 and
                        current_user.mentor.bq_2 and
                        current_user.mentor.hobbies and
                        current_user.mentor.lat and
                        current_user.mentor.long and
                        current_user.mentor.time_delta
                ):
                    current_user.mentor.ready = True
                    ready = True

                db.session.commit()
                flash('Your account has been updated!', 'success')
                return redirect(url_for('profile'))

    return render_template('userprofile.html', mentorform=form, menteeform=form2, ready=ready, find_form=find_form,
                           connect_form=connect_form, disconnect_form=disconnect_form, pot_mentors=pot_mentors)


@app.route("/admin-login")
def admin_login():
    return render_template('index.html')


@app.route("/admin-page")
@login_required(role="ADMIN")
def admin_page():
    return render_template('index.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
