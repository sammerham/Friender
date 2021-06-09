# run these tests like:
#
# python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Match
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

"""Match model tests."""


class MatchModelTestCase(TestCase):
    """Test match for matches."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        self.uid1 = 94566
        self.uid2 = 94522
        u1 = User.signup(**user1)
        u1.id = self.uid1
        u2 = User.signup(**user2)
        u2.id = self.uid2
        db.session.commit()

        self.u1 = User.query.get(self.uid1)
        self.u2 = User.query.get(self.uid2)

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback() 
    
    def test_Match_model(self):
        """Does basic model work?"""

        m = Match(match_to_id  =self.uid2, match_from_id=self.uid1)

        db.session.add(m)
        db.session.commit()

        # User1 should have 1 matcher
        self.assertEqual(len(self.u1.matchers),1 )
        self.assertEqual(len(self.u1.matching),0)
        self.assertEqual(len(self.u2.matchers), 0)
        self.assertEqual(len(self.u2.matching),1)
