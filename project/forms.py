from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import TextArea
from project.models import User
import phonenumbers
from flask_login import login_user, current_user, logout_user, login_required

expertise_l = [("Engineering", "Engineering"), ("Commerce", "Commerce"), ("Medical", "Medical"), ("Arts", "Arts")]
class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    # def validate_phone(self, phone):
    #     try:
    #         input_number = phonenumbers.parse(phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')
    #     except:
    #         input_number = phonenumbers.parse("+91" + phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MenteeForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    city = SelectField('city', choices=[('bangalore', 'Bangalore'), ('chennai', 'Chennai'), ('hyderabad', 'Hyderabad'),
                                        ('delhi', 'Delhi')])
    gender = SelectField('gender', choices=[("Prefer Not To Tell", "Prefer Not To Tell"), ('Male', 'Male'), ('Female', 'Female')])
    gender_pref = SelectField('gender preference', choices=[('Male', 'Male'), ('Female', 'Female')])
    language_pref = SelectField("language preference", choices=[("English", "English"), ("Hindi", "Hindi"), ("Kannada", "Kannada")])
    aspiration = SelectField('aspiration', choices=expertise_l)
    hobbies = TextAreaField("Tell us your hobbies", widget=TextArea(), validators=[DataRequired(), Length(min=2)])
    b1 = TextAreaField("Qusetion 1", widget=TextArea(), validators=[DataRequired(), Length(min=10)])
    b2 = TextAreaField("Qusetion 2", widget=TextArea(), validators=[DataRequired(), Length(min=10)])
    submit2 = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            if not(current_user and current_user.username == user.username):
                print(1)
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            if not (current_user and current_user.email == user.email):
                print(2)
                raise ValidationError('That email is taken. Please choose a different one.')

    # def validate_phone(self, phone):
    #     try:
    #         input_number = phonenumbers.parse(phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')
    #     except:
    #         input_number = phonenumbers.parse("+91" + phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')


class MentorForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=5, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    gender = SelectField('gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    city = SelectField('city', choices=[('bangalore', 'Bangalore'), ('chennai', 'Chennai'), ('hyderabad', 'Hyderabad'),
                                        ('delhi', 'Delhi')])
    language = SelectField('language', choices=[("English", "English"), ("Hindi", "Hindi"), ("Kannada", "Kannada")])
    expertise = SelectField('expertise', choices=expertise_l)
    hobbies = TextAreaField("Tell us your hobbies", widget=TextArea(), validators=[DataRequired(), Length(min=2)])
    b1 = TextAreaField("Qusetion 1", widget=TextArea(), validators=[DataRequired(), Length(min=2)])
    b2 = TextAreaField("Qusetion 2", widget=TextArea(), validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            if not (current_user and current_user.username == user.username):
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            if not (current_user and current_user.email == user.email):
                raise ValidationError('That email is taken. Please choose a different one.')

    # def validate_phone(self, phone):
    #     try:
    #         input_number = phonenumbers.parse(phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')
    #     except:
    #         input_number = phonenumbers.parse("+91" + phone.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number.')


class ContactForm(FlaskForm):
    name = StringField("Name")
    email = StringField("Email")
    subject = StringField("Subject")
    message = TextAreaField("Message")
    submit = SubmitField("Send")


class ConnectForm(FlaskForm):
    connect = SubmitField(label='Connect With Mentor')


class DisconnectForm(FlaskForm):
    disconnect = SubmitField(label='Disconnect!')