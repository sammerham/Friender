import os

from flask import Flask, request, redirect, render_template, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
import logging
from sqlalchemy.exc import IntegrityError
from botocore.exceptions import ClientError
from models import db, connect_db, User, Like, View, Match
import boto3
# Let's use Amazon S3
s3 = boto3.resource('s3')
# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

app = Flask(__name__)

CURR_USER_KEY = "curr_user"

database_url = os.environ.get('DATABASE_URL', 'postgresql:///friender')
database_url = database_url.replace("postgres://", "postgresql://")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

#################################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# def upload_file(file_name, bucket, object_name=None):

def upload_file():
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # # If S3 object_name was not specified, use file_name
    # if object_name is None:
    #     object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file("download.jpeg", "friender-images" , 'download12.jpeg')
        # data = open('download.jpeg', 'rb')
        # s3_client.Bucket('friender-images').put_object(Key='download.jpeg', Body=data)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# data = open('test.jpg', 'rb')
# s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)




@app.route('/aws')
def aws():
    upload_file()
    return jsonify(message="Deleted")

@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB.
    if username already taken send error message back.

    Respond with JSON like: {user: 
    {id, username, firstname, lastname, zipcode, radius, hobbies, interests}.
    """

    username = request.json["username"]
    password = request.json["password"]
    firstname = request.json["firstname"]
    lastname = request.json["lastname"]
    zipcode = request.json["zipcode"]
    radius = request.json["radius"]
   
    try:   
        user = User.signup(
        username=username,
        password=password,
        firstname=firstname,
        lastname=lastname,
        zipcode=zipcode,
        radius=radius
    )
        db.session.add(user)
        db.session.commit()

        do_login(user)
        serialized = user.serialize()
        # Return w/status code 201 --- return tuple (json, status)
        return(jsonify(user=serialized), 201)

    except IntegrityError as e:
        return (jsonify(Error="Bad Request Error"), 400)

@app.route('/login', methods=["POST"])
def login():
    """Handle user login.

    Login User.
    if username or password incorrect, send error message back.

    Respond with JSON like: {user: 
    {id, username, firstname, lastname, zipcode, radius, hobbies, interests}.
    """

    username = request.json["username"]
    password = request.json["password"]

    user = User.authenticate(
        username=username,
        password=password
    )

    if user:
        do_login(user)
        serialized = user.serialize()
        # Return w/status code 201 --- return tuple (json, status)
        return(jsonify(user=serialized), 200)
    
    else:
        return (jsonify(Error="Invalid username or password"), 400)

#################################################################

# User:
#     - getByZipcode() ORDER BY random (match by zipcode {WHERE})

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get data about a single user.

        Respond with JSON like: {user: 
        {id, username, firstname, lastname, zipcode, radius, hobbies, interests}}.
    """
    
    user = User.query.get_or_404(user_id)

    serialized = user.serialize()

    return jsonify(user=serialized)

@app.route('/users/<int:user_id>', methods=["PATCH"])
def update_user(user_id):
    """Update data about a single user.

        Respond with JSON like: {user: 
        {id, username, firstname, lastname, zipcode, radius, hobbies, interests}}.
    """
    
    user = User.query.get_or_404(user_id)

    username = request.json['username']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    zipcode = request.json['zipcode']
    radius = request.json['radius']
    hobbies = request.json['hobbies']
    interests = request.json['interests']

    user.username = username
    user.firstname  = firstname
    user.lastname = lastname
    user.zipcode = zipcode
    user.radius = radius
    user.hobbies = hobbies
    user.interests = interests

    db.session.commit()
    serialized = user.serialize()

    return jsonify(user=serialized)

@app.route('/users/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    """Delete data about a single user.

        Respond with JSON like: {message: 'Deleted'}.
    """

    user = User.query.get_or_404(user_id)
    db.session.delete(user)

    db.session.commit()

    return jsonify(message="Deleted")



@app.route('/users/<int:user_id>/zipcode')
def get_random_user_by_zipcode(user_id):
    """Get data about a single user.

        Respond with JSON like: {user: 
        {id, username, firstname, lastname, zipcode, radius, hobbies, interests}}.
    """
    
    user = User.getUserByZipcode(user_id)

    serialized = user.serialize()

    return jsonify(user=serialized)