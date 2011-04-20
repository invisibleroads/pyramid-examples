'Tests for user account management'
from auth.tests import TestTemplate
from auth.models import db, User, User_
from auth.libraries.tools import hash_string


class TestUsers(TestTemplate):

    def test_index(self):
        'Assert that the user index page shows how many accounts are on file'
        url = self.get_url('user_index')
        # Make sure that the user index page is visible
        self.assert_('%s users' % db.query(User).count() in self.app.get(url).body)

    def test_registration(self):
        'Make sure that registration works'
        url = self.get_url('user_register')
        username = password = nickname = 'mathematics'
        email = username + '@example.com'
        # Make sure the registration page appears properly
        self.assert_('Registration' in self.app.get(url))
        # Register
        self.app.post(url, dict(username=username, password=password, nickname=nickname, email=email))
        # Register with the same username but with different case
        self.app.post(url, dict(username=username.upper(), password=password, nickname=nickname + 'x', email=email + 'x'))
        # Register with the same nickname but with different case
        self.app.post(url, dict(username=username + 'x', password=password, nickname=nickname.upper(), email=email + 'x'))
        # Register with the same email but with different case
        self.app.post(url, dict(username=username + 'x', password=password, nickname=nickname + 'x', email=email.upper()))
        # Confirm registration
        self.app.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).first()[0]))
        # Make sure the person exists
        self.assertEqual(db.query(User).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        self.assertEqual(db.query(User_).filter_by(password_hash=hash_string(password)).count(), 0)

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
        self.assertJSON(self.login({'username': self.userN['username'], 'password': self.userN['password'] + 'x'}), 0)
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
