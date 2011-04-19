'Page access tests'
from pyramid.exceptions import Forbidden

from auth.tests import TestTemplate


class TestPageAccess(TestTemplate):

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
        self.login(self.userN)
        self.app.get(url)

    def test_privileged(self):
        'Make sure the protected page is visible only to super users'
        url = self.get_url('page_privileged')
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, self.app.get, url)
        # Make sure the view is not visible to normal users
        self.login(self.userN)
        self.assertRaises(Forbidden, self.app.get, url)
        # Make sure the view is visible to super users
        self.login(self.userS)
        self.app.get(url)