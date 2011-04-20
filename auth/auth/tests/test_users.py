'Tests for user account management'
import re

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
        # Update credentials
        username, password, nickname, email = ['0' + self.userN[x] for x in 'username', 'password', 'nickname', 'email']
        password_hash = hash_string(password)
        self.assertJSON(self.app.post(url, dict(token=token, username=username, password=password, nickname=nickname, email=email)), 1)
        # Make sure the credentials have not changed yet
        self.assertEqual(db.query(User).filter_by(username=username, password_hash=password_hash, nickname=nickname, email=email).count(), 0)
        # Make sure the credentials have changed after confirmation
        self.app.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(username=username, password_hash=password_hash, nickname=nickname, email=email).count(), 1)

        # Load people
        # user1 = db.query(User).filter_by(username=username_, password_hash=hash_string(password_), nickname=nickname_, email=email_).first()
        # user2 = db.query(User).filter_by(username=username + 'x').first()
        # Add SMSAddress
        # smsAddress = SMSAddress(emailSMS, user2.id)
        # db.add(smsAddress)
        # db.commit()
        # smsAddressID = smsAddress.id
        # Make sure that only the owner can update SMS information
        # self.app.post(url('user_login'), dict(username=username, password=password))
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='activate')), 0)
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='deactivate')), 0)
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='remove')), 0)
        # self.app.post(url('user_login'), dict(username=username + 'x', password=password))
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='activate')), 1)
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='deactivate')), 1)
        # self.assertJSON(self.app.post(url, dict(smsAddressID=smsAddressID, action='remove')), 1)

    def test_reset(self):
        'Make sure that resetting the password works'
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
