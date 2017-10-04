from flask import Flask, render_template, g
app = Flask(__name__)

from . import views, data, config

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.conn.close()


@app.route('/')
def hello_world():
    return render_template('hello.html')
