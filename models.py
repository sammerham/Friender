from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Like(db.Model) :
    """Connection of a liker <-> liked_user."""
    __tablename__ = 'likes'
    user_being_liked_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_liking_id= db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Match(db.Model) :
    """Connection of a user1 matches <-> user2 matches."""
    __tablename__ = 'matches'

    match_to_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    match_from_id= db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class View(db.Model) :
    """Connection of a viwer <-> viewed_user."""

    __tablename__ = 'views'

    user_being_viewed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_viewing_id= db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model) :
    """User in the system."""
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    firstname = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    
    lastname = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    zipcode = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    radius = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )
    hobbies = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    interests = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(  #TODO figure out how to use AWS to store image
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    likers = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Like.user_being_liked_id== id),
        secondaryjoin=(Like.user_liking_id == id)
    )
    liking = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Like.user_liking_id== id),
        secondaryjoin=(Like.user_being_liked_id == id)
    )


    viewers = db.relationship(
        "User",
        secondary="views",
        primaryjoin=(View.user_being_viewed_id== id),
        secondaryjoin=(View.user_viewing_id == id)
    )

    viewing = db.relationship(
        "User",
        secondary="views",
        primaryjoin=(View.user_viewing_id == id),
        secondaryjoin=(View.user_being_viewed_id == id)
    )


    matchers = db.relationship(
        "User",
        secondary="matches",
        primaryjoin=(Match.match_from_id == id),
        secondaryjoin =(Match.match_to_id == id)
    )

    matching = db.relationship(
        "User",
        secondary="matches",
        primaryjoin=(Match.match_to_id == id),
        secondaryjoin=(Match.match_from_id== id)
    )