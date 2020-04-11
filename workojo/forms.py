from wtforms import BooleanField, StringField, PasswordField, IntegerField, validators
from flask_wtf import FlaskForm

class CreateWorkout(FlaskForm):
    tag = StringField('Add a Description')

class AddExercise(FlaskForm):
    exercise_name = StringField('Exercise Name')
    set_number = IntegerField('Number of Sets')
    repetitions = IntegerField('Number of Reps')
    unit = StringField('Rep Unit')

class AddMacros(FlaskForm):
    carbs = IntegerField('Carbs')
    protein = IntegerField('Protein')
    fats = IntegerField('Fats')

class DietGoals(FlaskForm):
    daily_protein = IntegerField('Daily Protein Goal')
    daily_carbs = IntegerField('Daily Carbs Goal')
    daily_fats = IntegerField('Daily Fats Goal')