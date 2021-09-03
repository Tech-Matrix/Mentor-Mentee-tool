import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from project import app, db, bcrypt
from project.forms import RegistrationForm, LoginForm
from project.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')