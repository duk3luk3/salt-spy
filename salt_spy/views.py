from flask import Flask, render_template, redirect, url_for, g
from natsort import natsorted
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from . import app, data, config, db
from .model import Job, Return, Minion
import sys


@app.route('/')
def dashboard():
#    returns = db.session.query(Return).filter(Return.fun.in_(['state.apply', 'state.highstate'])).all()
    returns = db.session.query(Return).all()
    minions = Minion.from_returns(returns)

    minions_sorted = sorted(minions.values(), key=lambda m: m.apply_age() if m.apply_age() is not None else sys.maxsize)

    return render_template('hello.html', minions=minions_sorted, nav='dashboard')

@app.route('/minions')
def minions():
    returns = db.session.query(Return).all()
    minions = Minion.from_returns(returns)

    minions_sorted = natsorted(minions.values(), key=lambda m: m.mid)

    #print(len(minions), file=sys.stderr)
    return render_template('minions.html', minions=minions_sorted, nav='minions')

@app.route('/runs')
def runs():
    states = db.session.query(Return).order_by(Return.date.desc()).all()

    return render_template('runs.html', states=states, nav='runs')

@app.route('/jobs')
def jobs():
    jobs = db.session.query(Job).order_by(Job.jid.desc()).all()

    return render_template('jobs.html', jobs=jobs, nav='jobs')

@app.route('/update_cal')
def update_cal():
    returns = db.session.query(Return).all()
    minions = Minion.from_returns(returns)

    days = {}

    for minion in minions.values():
        day = minion.update_day()
        if day:
            if not day in days:
                days[day] = []
            days[day].append(minion.mid)

    return render_template('update_cal.html', days=days)

@app.route('/health')
def health():
    return redirect(url_for('minions'))


@app.route('/run/detail/<int:run_id>')
def run_details(run_id):
    db = get_db()
    run = db.query(StateRun).filter(StateRun.run_id == run_id).one()
    return render_template('run_detail.html', run=run, nav='run_details')
