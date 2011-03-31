'Tests'
import unittest
from pyramid import testing
from pyramid.config import Configurator
from pyramid.exceptions import Forbidden
from sqlalchemy import create_engine

from auth.models import initialize_sql, Post


class TestViews(unittest.TestCase):

    db = initialize_sql(create_engine('sqlite://'))

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_index(self):
        from auth.views import index
        request = testing.DummyRequest()
        info = index(request)

    def test_public(self):
        from auth.views import public as view
        # Make sure the view is visible to the public
        info = view(testing.DummyRequest())
        self.assertEqual(info['content'], 'Public')

    def test_protected(self):
        from auth.views import protected as view
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, view, testing.DummyRequest())
        # Make sure the view is visible to authenticated users
        self.config.testing_securitypolicy(userid='basic', permissive=False)
        info = view(testing.DummyRequest())
        self.assertEqual(info['content'], 'Protected')

    def test_privileged(self):
        from auth.views import privileged as view
        # Make sure the view is not visible to the public
        request = testing.DummyRequest()
        self.assertRaises(Forbidden, view, request)
        # Make sure the view is only visible to superusers
        self.config.testing_securitypolicy(userid='basic', permissive=False)
        self.assertRaises(Forbidden, view, testing.DummyRequest())
        self.config.testing_securitypolicy(userid='super', permissive=False)
        info = view(testing.DummyRequest())
        self.assertEqual(info['content'], 'Privileged')
