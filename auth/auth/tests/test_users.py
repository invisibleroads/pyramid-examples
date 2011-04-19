'Tests for user account management'
import transaction
from pyramid.exceptions import Forbidden

from auth.tests import TestTemplate
from auth.models import db, User
from auth.libraries.tools import hash_string


class TestUsers(TestTemplate):

    def test_login(self):
        'Make sure that login works'
        url = self.get_url('user_login')
        # url_ = self.get_url('user_update')
        url_ = '/protected'
        # Going to a protected page displays the login page
        self.assert_('value=Login' in self.app.get(url_).body)
        # Going directly to the login page stores the target url
        self.assert_(url_ in self.app.get(url, dict(url=url_)).body)
        # Bad credentials fail
        userB = self.userN.copy()
        userB['password'] += 'x'
        self.assertJSON(self.login(userB), 0)
        # Good credentials succeed
        self.assertJSON(self.login(self.userN), 1)

    def test_logout(self):
        'Make sure that logout works'
        url = self.get_url('user_logout')
        # url_ = self.get_url('user_index')
        url_ = '/'
        # Logging out redirects whether the user is authenticated or not
        self.assertEqual(url_, self.app.get(url, dict(url=url_)).location)
        self.login(self.userN)
        self.assertEqual(url_, self.app.get(url, dict(url=url_)).location)
