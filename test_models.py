# run these tests like:
#
# python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Like, View, Match
from sqlalchemy.exc import IntegrityError


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///friender-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

default_img="/static/images/warbler-hero.jpg"

user1 = {   
            'username':"testuser1",
            'password':"password",
            'firstname':"test1",
            'lastname':"test11",
            'zipcode':'12345',
            'radius':5
        }

user2 = {
            'username':"testuser2",
            'password':"password2",
            'firstname':"test2",
            'lastname':"test22",
            'zipcode':'56789',
            'radius':6
        }

"""User model tests."""


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback() 
    
    def test_user_model(self):
        """Does basic model work?"""
        u = User(**user1)
        db.session.add(u)
        db.session.commit()

        # User should have no likes & no views, no matches
        self.assertEqual(len(u.likers), 0)
        self.assertEqual(len(u.liking), 0)
        self.assertEqual(len(u.viewers), 0)
        self.assertEqual(len(u.viewing), 0)
        self.assertEqual(len(u.matchers), 0)
        self.assertEqual(len(u.matching), 0)


    def test_user_repr_method(self):
        """ Does the repr method work as expected """
        user = User(**user1)
        user.id = 1
        # self.user = user
        res = f"<User #{user.id}: testuser1, test1, test11, 12345>"
        self.assertEqual(user.__repr__(), res)

### Liking Tests ###
    def test_user_is_liking_False(self):
        """ Does is_following successfully detect when user1 is not liking user2 """
        u1 = User(**user1)
        u2 = User(**user2)
        db.session.add_all([u1,u2])

        db.session.commit()

        self.assertFalse((u1.is_liking(u2)))


    def test_user_is_liked_by_True(self):
        """ Does is_followed_by successfully detect when user1 is liked by user2"""
        u1 = User(**user1)
        u2 = User(**user2)
        db.session.add_all([u1,u2])

        u1.likers.append(u2)

        db.session.commit()

        self.assertTrue((u1.is_liked_by(u2)))

### Test Signup ###
    def test_valid_signup(self):
        u_test = User.signup(**user1)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testuser1")
        self.assertEqual(u_test.firstname, "test1")
        self.assertEqual(u_test.lastname, "test11")
        self.assertEqual(u_test.zipcode, "12345")
        self.assertEqual(u_test.radius, 5)
        self.assertEqual(u_test.image_url, default_img)
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$")) 

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "password", "firstname","lastname", "zipcode", 1)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("username", "", "firstname","lastname", "zipcode", 1)


### Test Authenticate ###
    def test_valid_authentication(self):
        u = User.signup(**user1)

        user_authenticate = User.authenticate(u.username, "password")
        self.assertTrue(user_authenticate)
        self.assertEqual(user_authenticate.username, 'testuser1')
    
    def test_invalid_username(self):
        u = User.signup(**user1)
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        u = User.signup(**user1)
        self.assertFalse(User.authenticate(u.username, "badpassword"))