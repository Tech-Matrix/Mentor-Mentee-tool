import os
from functools import wraps
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from project import app, db, bcrypt
from project.forms import RegistrationForm, LoginForm
from project.models import User
from flask_login import login_user, current_user, logout_user, login_required

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated():
               return app.login_manager.unauthorized()
            urole = app.login_manager.reload_user().get_urole()
            if ( (urole != role) and (role != "ANY")):
                return app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/login")
def login():
    return render_template('home.html')


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
    return render_template('login_mentor.html', form=form)


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
    return render_template('login_mentee.html', form=form)


@app.route("/register")
def register():
    return render_template('home.html')


@app.route("/register-mentor", methods=['GET', 'POST'])
def register_mentor():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data, email=form.email.data,
                    phone=form.phone.data, password=hashed_password, urole="MENTOR")
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account has been created! You are now logged in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('signupmentor.html', form=form)


@app.route("/register-mentee", methods=['GET', 'POST'])
def register_mentee():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data, email=form.email.data,
                    phone=form.phone.data, password=hashed_password, urole="MENTEE")
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account has been created! You are now logged in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('signupmentee.html', form=form)


@app.route("/profile")
@login_required(role="ANY")
def profile():
    return render_template('home.html')


@app.route("/admin-login")
def admin_login():
    return render_template('home.html')


@app.route("/admin-page")
@login_required(role="ADMIN")
def admin_page():
    return render_template('home.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
