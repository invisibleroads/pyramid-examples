'Tests for user account management'
import re

from auth.tests import TestTemplate
from auth.models import DBSession, User, User_, SMSAddress
from auth.libraries.tools import hash_string


class TestUsers(TestTemplate):

    def test_index(self):
        'Assert that the user index page shows how many accounts are on file'
        db = DBSession()
        url = self.get_url('user_index')
        # Make sure that the user index page is visible
        self.assert_('%s users' % db.query(User).count() in self.app.get(url).body)

    def test_registration(self):
        'Make sure that registration works'
        db = DBSession()
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
        self.app.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        # Make sure the user exists
        self.assertEqual(db.query(User).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        self.assertEqual(db.query(User_).filter_by(password_hash=hash_string(password)).count(), 0)

    def test_login(self):
        'Make sure that login works'
        url = self.get_url('user_login')
        url_ = self.get_url('user_update')
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
        url_ = self.get_url('user_index')
        # Logging out redirects whether the user is authenticated or not
        self.assertEqual(url_, self.app.get(url, dict(url=url_)).location)
        self.login(self.userN)
        self.assertEqual(url_, self.app.get(url, dict(url=url_)).location)

    def test_update(self):
        'Make sure that updating credentials works'
        db = DBSession()
        url = self.get_url('user_update')
        # Check that we only see the login page if the user is not logged in
        self.assert_('value=Login' in self.app.get(url).body)
        self.assert_('value=Login' in self.app.post(url).body)
        # Check that the update form is filled with the user's credentials
        self.login(self.userN)
        body = self.app.get(url).body
        self.assert_(self.userN['username'] in body)
        self.assert_(self.userN['nickname'] in body)
        self.assert_(self.userN['email'] in body)
        token = re.search("token = '(.*)'", body).group(1)
        # Updating credentials requires a token
        username, password, nickname, email = ['0' + self.userN[x] for x in 'username', 'password', 'nickname', 'email']
        password_hash = hash_string(password)
        self.assertJSON(self.app.post(url, dict(username=username, password=password, nickname=nickname, email=email)), 0)
        self.assertJSON(self.app.post(url, dict(token=token, username=username, password=password, nickname=nickname, email=email)), 1)
        # Make sure the credentials have not changed yet
        self.assertEqual(db.query(User).filter_by(username=username, password_hash=password_hash, nickname=nickname, email=email).count(), 0)
        # Make sure the credentials have changed after confirmation
        self.app.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(username=username, password_hash=password_hash, nickname=nickname, email=email).count(), 1)

    def test_update_smsAddress(self):
        'Make sure that updating smsAddresses works'
        db = DBSession()
        url = self.get_url('user_update')
        # Get token
        self.login(self.userN)
        body = self.app.get(url).body
        token = re.search("token = '(.*)'", body).group(1)
        # Add an smsAddress that is not a valid email address
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='add', smsAddressEmail='xxx')), 0)
        # Add an smsAddress that is a valid email address
        self.login(self.userN)
        smsAddressEmail = 'sms1@example.com'
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='add', smsAddressEmail=smsAddressEmail)), 1)
        smsAddress1 = db.query(SMSAddress).filter_by(email=smsAddressEmail).first()
        self.login(self.userS)
        smsAddressEmail = 'sms2@example.com'
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='add', smsAddressEmail=smsAddressEmail)), 1)
        smsAddress2 = db.query(SMSAddress).filter_by(email=smsAddressEmail).first()
        self.login(self.userN)
        # Activate an smsAddress that doesn't belong to the user
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='activate', smsAddressID=smsAddress2.id, smsAddressCode=smsAddress2.code)), 0)
        # Activate an smsAddress with a bad code
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='activate', smsAddressID=smsAddress1.id, smsAddressCode=smsAddress1.code + 'x')), 0)
        # Activate an smsAddress with a good code
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='activate', smsAddressID=smsAddress1.id, smsAddressCode=smsAddress1.code)), 1)
        # Remove an smsAddress that doesn't belong to the user
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='remove', smsAddressID=smsAddress2.id)), 0)
        # Remove an smsAddress that does belong to the user
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='remove', smsAddressID=smsAddress1.id)), 1)
        # Send an invalid command
        self.assertJSON(self.app.post(url, dict(token=token, smsAddressAction='xxx')), 0)

    def test_reset(self):
        'Make sure that resetting the password works'
        db = DBSession()
        url = self.get_url('user_reset')
        email = self.userN['email']
        password_hash = hash_string(self.userN['password'])
        # Trying to reset an email that does not exist returns an error
        self.assertJSON(self.app.post(url, dict(email=email + 'x')), 0)
        # Resetting the password does not immediately change the password
        self.assertJSON(self.app.post(url, dict(email=email)), 1)
        self.assertEqual(db.query(User).filter_by(email=email, password_hash=password_hash).count(), 1)
        # Apply change
        self.app.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(email=email, password_hash=password_hash).count(), 0)
