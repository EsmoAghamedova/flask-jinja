from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length

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
    
class ResendForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Create account')
    
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Reset password')
    
class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Update password')

class TipForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    body = TextAreaField('Content', validators=[DataRequired()])
    category = StringField('Category', validators=[Length(max=80)])
    submit = SubmitField('Save')

class AdminUserForm(FlaskForm):
    is_admin = BooleanField('Admin privileges')
    submit = SubmitField('Update role')


class ActionForm(FlaskForm):
    submit = SubmitField('Confirm')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Save changes')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Update password')


class ResetProgressForm(FlaskForm):
    category = SelectField(
        'Reset category',
        choices=[
            ('all', 'All progress'),
            ('moods', 'Mood entries'),
            ('todos', 'To-dos'),
            ('habits', 'Habits'),
        ],
        validators=[DataRequired()],
    )
    confirm = BooleanField('I understand this action cannot be undone', validators=[InputRequired()])
    submit = SubmitField('Reset progress')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = BooleanField('I understand my account will be deleted', validators=[InputRequired()])
    submit = SubmitField('Delete account')
