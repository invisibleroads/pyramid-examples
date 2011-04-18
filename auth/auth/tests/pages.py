'Page access tests'
import unittest
from pyramid import testing
from pyramid.exceptions import Forbidden
from sqlalchemy import create_engine

from auth.models import initialize_sql


class TestPageAccess(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        initialize_sql(create_engine('sqlite://'))

    def tearDown(self):
        testing.tearDown()

    def test_public(self):
        from auth.views.pages import public as view
        # Make sure the view is visible to the public
        view(testing.DummyRequest())

    def test_protected(self):
        from auth.views.pages import protected as view
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, view, testing.DummyRequest())
        # Make sure the view is visible to authenticated users
        self.config.testing_securitypolicy(userid=1, permissive=False)
        view(testing.DummyRequest())

    def test_privileged(self):
        from auth.views.pages import privileged as view
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, view, testing.DummyRequest())
        # Make sure the view is not visible to normal users
        self.config.testing_securitypolicy(userid=1, permissive=False)
        self.assertRaises(Forbidden, view, testing.DummyRequest())
        # Make sure the view is visible to super users
        self.config.testing_securitypolicy(userid=1, groupids=['super'], permissive=False)
        view(testing.DummyRequest())
