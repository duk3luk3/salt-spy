from flask import Flask, render_template, g
from flask_sqlalchemy import SQLAlchemy
from . import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config.config.DB
db = SQLAlchemy(app)

from . import views, data


