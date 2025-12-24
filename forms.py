from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length

MOOD_CHOICES = [
    ('Happy', 'Happy'),
    ('Content', 'Content'),
    ('Neutral', 'Neutral'),
    ('Sad', 'Sad'),
    ('Anxious', 'Anxious'),
    ('Excited', 'Excited'),
]

FREQUENCY_CHOICES = [
    ('Daily', 'Daily'),
    ('Weekly', 'Weekly'),
    ('Monthly', 'Monthly'),
    ('Custom', 'Custom'),
]

class MoodForm(FlaskForm):
    mood = SelectField('Mood', validators=[DataRequired(), Length(max=120)], choices=MOOD_CHOICES)
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')

class ToDoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired(), Length(max=255)])
    detail = TextAreaField('Detail')
    done = BooleanField('Done')
    submit = SubmitField('Save')

class HabitTrackerForm(FlaskForm):
    habit = StringField('Habit', validators=[DataRequired(), Length(max=255)])
    frequency = SelectField('Frequency', validators=[Length(max=64)], choices=FREQUENCY_CHOICES)
    submit = SubmitField('Save')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Create account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class TipForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    body = TextAreaField('Content', validators=[DataRequired()])
    category = StringField('Category', validators=[Length(max=80)])
    submit = SubmitField('Save')


class AdminUserForm(FlaskForm):
    is_admin = BooleanField('Admin privileges')
    submit = SubmitField('Update role')
