from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func

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
    """Connection of a viewer <-> viewed_user."""

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

# TODO add model methods
class User(db.Model) :
    """User in the system."""
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
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
    )
    
    lastname = db.Column(
        db.Text,
        nullable=False,
    )
    zipcode = db.Column(
        db.Text,
        nullable=False,
    )

    radius = db.Column(
        db.Integer,
        nullable=False,
    )

    hobbies = db.Column(
        db.Text,
    )

    interests = db.Column(
        db.Text,
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

    def serialize(self):
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "zipcode": self.zipcode,
            "radius": self.radius,
            "hobbies": self.hobbies,
            "interests": self.interests
        }

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.password} {self.firstname}, {self.lastname}, {self.zipcode}>"
        

    def is_liked_by(self, other_user):
        """Is this user liked by `other_user`?"""

        found_user_list = [
            user for user in self.likers if user == other_user]
        return len(found_user_list) == 1

    def is_liking(self, other_user):
        """Is this user liking `other_use`?"""

        found_user_list = [
            user for user in self.liking if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, password, firstname, lastname, zipcode, radius ):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            firstname=firstname,
            lastname=lastname,
            zipcode=zipcode,
            radius=radius,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        print("User --->", user)

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def getUserByZipcode(cls, user_id):
        """Find user within same zipcode of this user`."""
        current_user = cls.query.get(user_id)
        user = User.query.filter(User.zipcode == current_user.zipcode).order_by(func.random()).first()
        if(user.id != user_id):
            return user

# todo check on edge cases with getting user by zipcode.  


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)