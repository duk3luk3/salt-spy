from flask import Flask, render_template, redirect, url_for, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import app, data, config
from .model import Minion, StateRun, StateExecution

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
    minions = db.query(Minion)
    minions=[
        dict(name=m.name,
            runs=[
                dict(id=r.run_id, user=r.user, ret_time=r.ret_time, sls=r.sls(), test=r.is_test,
                    states=[
                        dict(id=s.state_id,run_num=s.run_num, sls=s.sls, function=s.function, result=s.result, name=s.name, comment=s.comment)
                        for s in r.states])
                for r in m.runs])
        for m in minions]
    return render_template('minions.html', minions=minions[:1], nav='minions')

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
