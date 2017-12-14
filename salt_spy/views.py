from flask import Flask, render_template, redirect, url_for, g, request
from natsort import natsorted
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from . import app, data, config, db, utils
from .model import Job, Return, Minion
import sys


@app.route('/')
def dashboard():
#    returns = db.session.query(Return).filter(Return.fun.in_(['state.apply', 'state.highstate'])).all()
    returns = db.session.query(Return).all()
    minions = Minion.from_returns(returns)

    minions_sorted = sorted(minions.values(), key=lambda m: m.apply_age() if m.apply_age() is not None else sys.maxsize)

    return render_template('hello.html', minions=minions_sorted, nav='dashboard')


def render_collection(cls, name, order_by):
    id_ = request.args.get('id')
    limit = request.args.get('limit', default=config.config.LIMIT, type=int)
    if id_:
        ids = id_.split(',')
        pk = cls.__mapper__.primary_key[0]
        data = db.session.query(cls).filter(pk.in_(ids)).order_by(order_by).all()
    elif limit:
        data = db.session.query(cls).order_by(order_by).limit(limit).all()
    else:
        data = db.session.query(cls).order_by(order_by).all()

    kwargs = {
            'nav': name,
            name: data
            }

    return render_template(name+'.html', **kwargs)


@app.route('/minions')
def minions():
    id_ = request.args.get('id')
    if id_:
        ids = id_.split(',')
        returns = db.session.query(Return).filter(Return.mid.in_(ids)).all()
    else:
        returns = db.session.query(Return).all()

    minions = Minion.from_returns(returns)
    minions_sorted = natsorted(minions.values(), key=lambda m: m.mid)

    #print(len(minions), file=sys.stderr)
    return render_template('minions.html', minions=minions_sorted, nav='minions')

@app.route('/runs')
def runs():
    return render_collection(Return, 'runs', Return.date.desc())
#    id_ = request.args.get('id')
#    if id_:
#        states = [db.session.query(Return).get(id_)]
#    else:
#        states = db.session.query(Return).order_by(Return.date.desc()).all()
#
#    return render_template('runs.html', states=states, nav='runs')

@app.route('/jobs')
def jobs():
    return render_collection(Job, 'jobs', Job.jid.desc())
#    jobs = db.session.query(Job).order_by(Job.jid.desc()).all()
#
#    return render_template('jobs.html', jobs=jobs, nav='jobs')

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

    today, this_month, next_month = utils.get_calendar()

    return render_template('update_cal.html', days=days, today=today, this_month=this_month, next_month=next_month)

@app.route('/health')
def health():
    return redirect(url_for('minions'))


@app.route('/run/detail/<int:run_id>')
def run_details(run_id):
    run = db.session.query(StateRun).filter(StateRun.run_id == run_id).one()
    return render_template('run_detail.html', run=run, nav='run_details')
