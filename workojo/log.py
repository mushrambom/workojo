from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from workojo.auth import login_required
from workojo.db import get_db
from workojo.forms import CreateWorkout, AddExercise, AddMacros, DietGoals
from workojo._log_helper import (
    emoji_list, quote_list, kcal_counter, get_exercise, get_macros, get_workout, 
    distance_from_goals, get_goals
)
from random import choice
import datetime

bp = Blueprint('log', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    quote = choice(quote_list)
    emoji = choice(emoji_list)
    db = get_db()
    user_id = session.get('user_id')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM workout WHERE creator_id=?', (user_id,))
    results = cursor.fetchall()
    count = len(results)
    per_page = 10 # define how many results you want per page
    page = request.args.get('page', 1, type=int)
    pages = count // per_page # this is the number of pages
    offset = (page-1)*per_page # offset for SQL query
    limit = 20 if page == pages else per_page # limit for SQL query
    prev_url = url_for('log.paginated_index', page=page-1) if page > 1 else None
    next_url = url_for('log.paginated_index', page=page+1) if page < pages else None
    workouts = db.execute(
        'SELECT w.id, created, tag, creator_id'
        ' FROM workout w JOIN user u ON w.creator_id=u.id'
        ' WHERE creator_id= ?'
        ' ORDER BY created DESC'
        ' LIMIT ? OFFSET ?',(user_id, limit, offset)
    ).fetchall()
    return render_template('log/index.html', workouts=workouts, user_id=user_id, quote=quote, emoji=emoji,
    prev_url=prev_url, next_url=next_url)

@bp.route('/<int:page>/index')
def paginated_index(page):
    quote = choice(quote_list)
    emoji = choice(emoji_list)
    db = get_db()
    user_id = session.get('user_id')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM workout WHERE creator_id=?', (user_id,))
    results = cursor.fetchall()
    count = len(results)
    per_page = 10 # define how many results you want per page
    page = page
    pages = count // per_page # this is the number of pages
    offset = (page-1)*per_page # offset for SQL query
    limit = 20 if page == pages else per_page # limit for SQL query
    prev_url = url_for('log.paginated_index', page=page-1) if page > 1 else None
    next_url = url_for('log.paginated_index', page=page+1) if page < pages else None
    workouts = db.execute(
        'SELECT w.id, created, tag, creator_id'
        ' FROM workout w JOIN user u ON w.creator_id=u.id'
        ' WHERE creator_id= ?'
        ' ORDER BY created DESC'
        ' LIMIT ? OFFSET ?',(user_id, limit, offset)
    ).fetchall()
    return render_template('log/index.html', workouts=workouts, user_id=user_id, quote=quote, emoji=emoji,
    prev_url=prev_url, next_url=next_url)

@bp.route('/<int:id>/workout')
@login_required
def workout(id):
    db = get_db()
    workout = get_workout(id)
    user_id = session.get('user_id')
    exercises = db.execute(
        'SELECT e.id, exercise_name, set_number, repetitions, unit, created, workout_id'
        ' FROM exercise e JOIN workout w ON e.workout_id=w.id'
        ' WHERE workout_id= ?',(id,)
    ).fetchall()
    macros = db.execute(
        'SELECT m.id, carbs, protein, fats, workout_id'
        ' FROM macros m JOIN workout w on m.workout_id=w.id'
        ' WHERE workout_id = ?',(id,)
    ).fetchone()
    workout = db.execute(
        'SELECT *'
        ' FROM workout'
        ' ORDER BY created DESC'
        ).fetchone()
    diet_goals = db.execute(
        'SELECT d.creator_id, daily_protein, daily_fats, daily_carbs'
        ' FROM diet_goals d JOIN user u on d.creator_id=u.id'
        ' WHERE creator_id = ?',(user_id,)
    ).fetchone()
    distance_list = distance_from_goals(diet_goals, macros)
    session['current_id'] = workout['id']
    kcal = kcal_counter(macros)
    return render_template('log/workout_details.html', macros=macros, exercises=exercises, workout=workout,
    user_id=user_id, kcal=kcal, distance_list=distance_list, diet_goals=diet_goals)

#options for select forms
unit_list = ['reps', 'seconds', 'minutes']

@bp.route('/create_workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    form = CreateWorkout(request.form)
    if request.method == 'POST' and form.validate():
        tag = form.tag.data
        db = get_db()
        if tag != '':
            db.execute(
                'INSERT INTO workout(creator_id, tag)'
                ' VALUES (?, ?)',
                (g.user['id'], tag)
            )
            db.commit()
            workout = db.execute(
                'SELECT *'
                ' FROM workout'
                ' ORDER BY created DESC'
                ).fetchone()
            return redirect(url_for('log.workout', id=workout['id']))
        flash('Please, fill description field.')
    return render_template('log/create_workout.html', form=form)

@bp.route('/diet_goals', methods=['GET', 'POST'])
@login_required
def diet_goals():
    diet_goals = get_goals(g.user['id'])
    if diet_goals:
        return redirect(url_for('log.show_goals'))
    else:
        form = DietGoals()
        if form.validate_on_submit():
            db = get_db()
            db.execute(
                'INSERT INTO diet_goals(creator_id, daily_protein, daily_carbs, daily_fats)'
                ' VALUES(?, ?, ?, ?)',
                (g.user['id'], form.daily_protein.data, form.daily_carbs.data, form.daily_fats.data)
                )
            db.commit()
            return redirect(url_for('log.index'))
        return render_template('log/diet_goals.html', form=form)

@bp.route('/show_goals')
@login_required
def show_goals():
    db = get_db()
    diet_goals = db.execute(
        'SELECT creator_id, daily_protein, daily_carbs, daily_fats, created'
        ' FROM diet_goals'
        ' WHERE creator_id = ?',(g.user['id'],)).fetchone()
    if diet_goals:
        kcal = diet_goals['daily_protein'] * 4 + diet_goals['daily_fats'] * 9 + diet_goals['daily_carbs'] * 4
        return render_template('log/show_goals.html', diet_goals=diet_goals, kcal=kcal)
    else:
        return redirect(url_for('log.diet_goals'))

@bp.route('/update_goals', methods=('GET', 'POST'))
@login_required
def update_goals():
    diet_goals = get_goals(g.user['id'])
    form = DietGoals()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'UPDATE diet_goals SET daily_protein = ?, daily_carbs = ?, daily_fats = ?, created = ?'
            ' WHERE creator_id = ?',
            (form.daily_protein.data, form.daily_carbs.data, form.daily_fats.data, datetime.datetime.now(), g.user['id'])
        )
        db.commit()
        return redirect(url_for('log.show_goals'))
    return render_template('log/diet_goals.html', form=form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = AddExercise(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        exercise_name = form.exercise_name.data
        set_number = form.set_number.data
        repetitions = form.repetitions.data
        unit = request.form['unit']
        db.execute(
            'INSERT INTO exercise(exercise_name, set_number, repetitions, unit, workout_id)'
            ' VALUES (?, ?, ?, ?, ?)',
            (exercise_name, set_number, repetitions, unit, session['current_id'])
        )
        db.commit()
        return redirect(url_for('log.workout', id=session['current_id']))
    flash('Please, fill every field correctly. Only positive numbers are accepted as set number and repetitions')
    return render_template('log/create.html', unit_list=unit_list, form=form)

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    exercise = get_exercise(id)
    form = AddExercise(request.form)
    if form.validate_on_submit():
        exercise_name = form.exercise_name.data
        set_number = form.set_number.data
        repetitions = form.repetitions.data
        unit = request.form['unit']
        error = None

        if not exercise_name or not set_number or not repetitions or not unit:
            error = 'All fields beside body are necessary'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE exercise SET exercise_name = ?, set_number = ?, repetitions = ?, unit = ?'
                ' WHERE id = ?',
                (exercise_name, set_number, repetitions, unit, id)
            )
            db.commit()
            return redirect(url_for('log.workout', id=exercise['workout_id']))
    elif request.method == 'GET':
        form.exercise_name.data = exercise['exercise_name']
        form.set_number.data = exercise['set_number']
        form.repetitions.data = exercise['repetitions']
        form.unit.data = exercise['unit']
        return render_template('log/update.html', exercise=exercise, unit_list=unit_list, form=form)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    exercise = get_exercise(id)
    db = get_db()
    db.execute(
        'DELETE FROM exercise WHERE id = ?', (id, )
    )
    db.commit()
    return redirect(url_for('log.workout', id=exercise['workout_id']))

@bp.route('/macro_create', methods=('GET', 'POST'))
@login_required
def macro_create():
    form = AddMacros()
    if form.validate_on_submit():
        db = get_db()
        db.execute(
            'INSERT INTO macros(carbs, protein, fats, workout_id)'
            ' VALUES (?, ?, ?, ?)',
            (form.carbs.data, form.protein.data, form.fats.data, session['current_id'])
        )
        db.commit()
        return redirect(url_for('log.workout', id=session['current_id']))
    return render_template('log/macro_create.html', form=form)

@bp.route('/<int:id>/macro_update', methods=('GET', 'POST'))
@login_required
def macro_update(id):
    macros = get_macros(id)
    form = AddMacros(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        db.execute(
            'UPDATE macros SET carbs = ?, protein = ?, fats = ?'
            ' WHERE id = ?',(form.carbs.data, form.protein.data, form.fats.data, id)
        )
        db.commit()
        return redirect(url_for('log.workout', id=macros['workout_id']))
    return render_template('log/macro_create.html', form=form)






