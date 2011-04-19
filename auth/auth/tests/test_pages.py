'Page access tests'
import webtest
import unittest
import transaction
from pyramid.exceptions import Forbidden

from auth import main
from auth.models import db, User
from auth.libraries.tools import hash_string


class TestPageAccess(unittest.TestCase):

    router = main({}, **{'sqlalchemy.url': 'sqlite://'})

    def setUp(self):
        self.app = webtest.TestApp(self.router)
        self.app.post(self.get_url('user_logout'))
        self.userN = {'username': 'userN', 'password': 'password'}
        self.userS = {'username': 'userS', 'password': 'password'}
        if db.query(User).count() == 2:
            for valueByKey in self.userN, self.userS:
                username, password = [valueByKey.get(x) for x in 'username', 'password']
                db.add(User(
                    username=username, 
                    password_hash=hash_string(password), 
                    nickname=unicode(username),
                    email='%s@example.com' % username,
                    is_super='S' in username))
            transaction.commit()

    def get_url(self, name):
        'Return URL for route'
        return self.router.routes_mapper.generate(name, {})

    def test_public(self):
        'Make sure the public page is visible without authentication'
        url = self.get_url('page_public')
        # Make sure the view is visible to the public
        self.app.get(url)

    def test_protected(self):
        'Make sure the protected page is visible only after authentication'
        url = self.get_url('page_protected')
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, self.app.get, url)
        # Make sure the view is visible to normal users
        self.app.post(self.get_url('user_login'), self.userN)
        self.app.get(url)

    def test_privileged(self):
        'Make sure the protected page is visible only to super users'
        url = self.get_url('page_privileged')
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, self.app.get, url)
        # Make sure the view is not visible to normal users
        self.app.post(self.get_url('user_login'), self.userN)
        self.assertRaises(Forbidden, self.app.get, url)
        # Make sure the view is visible to super users
        self.app.post(self.get_url('user_login'), self.userS)
        self.app.get(url)
