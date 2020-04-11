from workojo.db import get_db
from flask import g

quote_list = ['In training, you listen to your body. In competition, you tell your body to shut up.',
'You shall gain, but you shall pay with sweat, blood, and vomit.',
'There’s no secret formula. I lift heavy, work hard, and aim to be the best.', 
'Don’t be afraid of failure. This is the way to succeed.' ]
emoji_list = ['🏋️', '🧘', '💪']

def kcal_counter(macros):
    if macros:
        kcal = (macros['fats'] * 9) + (macros['carbs'] * 4) + (macros['protein'] * 4)
    else:
        kcal = 0
    return kcal

def distance_from_goals(diet_goals, macros):
    if diet_goals and macros:
        protein_distance = diet_goals['daily_protein'] - macros['protein']
        carb_distance = diet_goals['daily_carbs'] - macros['carbs']
        fats_distance = diet_goals['daily_fats'] - macros ['fats']
        distance_list = [protein_distance, carb_distance, fats_distance]
        return distance_list

def get_workout(id, check_author=True):
    workout = get_db().execute(
        'SELECT w.id, creator_id, created, tag, created, username'
        ' FROM workout w JOIN user u ON w.creator_id=u.id'
        ' WHERE w.id = ?',
        (id,)
    ).fetchone()
    if workout is None:
        abort(404, 'Workout id {0} does not exist.'.format(id))
    if check_author and workout['creator_id'] != g.user['id']:
        abort(403)
    return workout

def get_exercise(id, check_author=True):
    exercise = get_db().execute(
        'SELECT e.id, exercise_name, set_number, repetitions, unit, workout_id, creator_id'
        ' FROM exercise e JOIN workout w ON e.workout_id=w.id'
        ' WHERE e.id = ?',
        (id,)
    ).fetchone()
    if exercise is None:
        abort(404, 'Exercise id {0} does not exist.'.format(id))
    if check_author and exercise['creator_id'] != g.user['id']:
        abort(403)
    return exercise

def get_macros(id, check_author=True):
    macros = get_db().execute(
        'SELECT m.id, carbs, protein, fats, workout_id, creator_id'
        ' FROM macros m JOIN workout w ON m.workout_id=w.id'
        ' WHERE m.id = ?',(id,)
    ).fetchone()
    if macros == None:
        abort(404, 'No macro associated with this workout')
    if check_author and macros['creator_id'] != g.user['id']:
        abort(403)
    return macros

def get_goals(id, check_author=True):
    goals = get_db().execute(
        'SELECT g.daily_protein, daily_carbs, daily_fats, created, creator_id'
        ' FROM diet_goals g JOIN user u ON g.creator_id=u.id'
        ' WHERE g.creator_id = ?',(id,)
    ).fetchone()
    return goals