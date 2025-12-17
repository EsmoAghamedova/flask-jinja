from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class MoodForm(FlaskForm):
    mood = SelectField('How are you feeling today?', 
                       choices=[('happy', '😊 Happy'), 
                                ('sad', '😢 Sad'), 
                                ('anxious', '😰 Anxious'), 
                                ('angry', '😡 Angry'), 
                                ('neutral', '😐 Neutral')],
                       validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Length(max=200)])
    submit = SubmitField('Submit')
    
class ToDoForm(FlaskForm):
    task = StringField('New Task', validators=[DataRequired(), Length(max=100)])
    detail = TextAreaField('Task Details', validators=[Length(max=300)])
    submit = SubmitField('Add Task')
    
class HabitTrackerForm(FlaskForm):
    habit = StringField('Habit Name', validators=[DataRequired(), Length(max=50)])
    frequency = SelectField('Frequency', 
                            choices=[('daily', 'Daily'), 
                                     ('weekly', 'Weekly'), 
                                     ('monthly', 'Monthly')],
                            validators=[DataRequired()])
    submit = SubmitField('Track Habit')

    