import os

import pdb

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Like, View, Match

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL', 'postgresql:///friender')
database_url = database_url.replace("postgres://", "postgresql://")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)