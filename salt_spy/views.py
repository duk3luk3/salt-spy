from flask import Flask, render_template, redirect, url_for, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import app, data, config
from .model import Job, Return, Minion
import sys

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'engine'):
        db_file = config.config.DB
        g.engine = create_engine('sqlite:///' + db_file)
        g.Session = sessionmaker(bind=g.engine)
    return g.Session()

@app.route('/')
def hello_world():
    return render_template('hello.html', nav='home')

@app.route('/minions')
def minions():
    db = get_db()
    returns = db.query(Return).all()

    print(returns, file=sys.stderr)

    minions = Minion.from_returns(returns)

    print(len(minions), file=sys.stderr)
    return render_template('minions.html', minions=minions.values(), nav='minions')

@app.route('/states')
def states():
    return redirect(url_for('minions'))

@app.route('/health')
def health():
    return redirect(url_for('minions'))



@app.route('/run/detail/<int:run_id>')
def run_details(run_id):
    db = get_db()
    run = db.query(StateRun).filter(StateRun.run_id == run_id).one()
    return render_template('run_detail.html', run=run, nav='run_details')
