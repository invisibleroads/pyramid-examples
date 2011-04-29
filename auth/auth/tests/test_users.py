'Tests for user account management'
from auth.tests import TestTemplate, ReplaceableDict, get_token
from auth.models import db, User, User_, SMSAddress
from auth.libraries.tools import hash


class TestUsers(TestTemplate):

    def test_index(self):
        'Assert that the user index page shows how many accounts are on file'
        url = self.get_url('user_index')
        # Make sure that the user index page is visible
        self.assert_('%s users' % db.query(User).count() in self.get(url).unicode_body)

    def test_registration(self):
        'Make sure that registration works'
        url = self.get_url('user_register')
        username, password, nickname, email = [self.userN[x].replace('2', '3') for x in 'username', 'password', 'nickname', 'email']
        params = ReplaceableDict(username=username, password=password, nickname=nickname, email=email)
        # Make sure the registration page appears properly
        self.assert_('Registration' in self.get(url).unicode_body)
        # Register
        self.post(url, params)
        # Register with the same username but with different case
        self.post(url, params.replace(username=username.upper(), nickname=nickname + 'x', email=email + 'x'))
        # Register with the same nickname but with different case
        self.post(url, params.replace(username=username + 'x', nickname=nickname.upper(), email=email + 'x'))
        # Register with the same email but with different case
        self.post(url, params.replace(username=username + 'x', nickname=nickname + 'x', email=email.upper()))
        # Confirm registration
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        # Make sure the user exists
        self.assertEqual(db.query(User).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        self.assertEqual(db.query(User_).filter_by(password_=hash(password)).count(), 0)

    def test_login(self):
        'Make sure that login works'
        url = self.get_url('user_login')
        url_ = self.get_url('user_update')
        # Going to a protected page displays the login page
        self.assert_('value=Login' in self.get(url_).unicode_body)
        # Going directly to the login page stores the target url
        self.assert_(url_ in self.get(url, dict(url=url_)).unicode_body)
        # Bad credentials fail
        self.assertJSON(self.login({'username': self.userN['username'], 'password': self.userN['password'] + 'x'}), 0)
        # Good credentials succeed
        self.assertJSON(self.login(self.userN), 1)

    def test_logout(self):
        'Make sure that logout works'
        url = self.get_url('user_logout')
        url_ = self.get_url('user_index')
        # Logging out redirects whether the user is authenticated or not
        self.assertEqual(url_, self.get(url, dict(url=url_)).location)
        self.login(self.userN)
        self.assertEqual(url_, self.get(url, dict(url=url_)).location)

    def test_update(self):
        'Make sure that updating credentials works'
        url = self.get_url('user_update')
        # Check that we only see the login page if the user is not logged in
        self.assert_('value=Login' in self.get(url).unicode_body)
        self.assert_('value=Login' in self.post(url).unicode_body)
        # Check that the update form is filled with the user's credentials
        self.login(self.userN)
        body = self.get(url).unicode_body
        self.assert_(self.userN['username'] in body)
        self.assert_(self.userN['nickname'] in body)
        self.assert_(self.userN['email'].lower() in body)
        token = get_token(body)
        # Updating credentials requires a token
        username, password, nickname, email = ['0' + self.userN[x] for x in 'username', 'password', 'nickname', 'email']
        password_ = hash(password)
        params = ReplaceableDict(token=token, username=username, password=password, nickname=nickname, email=email)
        self.assertJSON(self.post(url, params.replace(token='')), 0)
        self.assertJSON(self.post(url, params), 1)
        # Make sure the credentials have not changed yet
        self.assertEqual(db.query(User).filter_by(username=username, password_=password_, nickname=nickname, email=email).count(), 0)
        # Make sure the credentials have changed after confirmation
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(username=username, password_=password_, nickname=nickname, email=email).count(), 1)

    def test_update_smsAddress(self):
        'Make sure that updating smsAddresses works'
        url = self.get_url('user_update')
        # Get token
        self.login(self.userN)
        token = get_token(self.get(url).unicode_body)

        params = ReplaceableDict(token=token, smsAddressAction='add', smsAddressEmail='xxx@example.com')
        # Add an smsAddress that is not a valid email address
        self.assertJSON(self.post(url, params.replace(smsAddressEmail='xxx')), 0)
        # Add an smsAddress that is a valid email address
        self.login(self.userN)
        smsAddressEmail = 'sms1@example.com'
        self.assertJSON(self.post(url, params.replace(smsAddressEmail=smsAddressEmail)), 1)
        smsAddress1 = db.query(SMSAddress).filter_by(email=smsAddressEmail).first()
        self.login(self.userS)
        smsAddressEmail = 'sms2@example.com'
        self.assertJSON(self.post(url, params.replace(smsAddressEmail=smsAddressEmail)), 1)
        smsAddress2 = db.query(SMSAddress).filter_by(email=smsAddressEmail).first()
        # Add a duplicate smsAddress
        self.assertJSON(self.post(url, params), 1)
        self.assertJSON(self.post(url, params), 0)

        params = ReplaceableDict(token=token, smsAddressAction='activate', smsAddressID=smsAddress1.id, smsAddressCode=smsAddress1.code)
        self.login(self.userN)
        # Activate an smsAddress that doesn't belong to the user
        self.assertJSON(self.post(url, params.replace(smsAddressID=smsAddress2.id, smsAddressCode=smsAddress2.code)), 0)
        # Activate an smsAddress with a bad code
        self.assertJSON(self.post(url, params.replace(smsAddressCode=smsAddress1.code + 'x')), 0)
        # Activate an smsAddress with a good code
        self.assertJSON(self.post(url, params), 1)

        params = ReplaceableDict(token=token, smsAddressAction='remove', smsAddressID=smsAddress1.id)
        # Remove an smsAddress that doesn't belong to the user
        self.assertJSON(self.post(url, params.replace(smsAddressID=smsAddress2.id)), 0)
        # Remove an smsAddress that does belong to the user
        self.assertJSON(self.post(url, params), 1)

        params = ReplaceableDict(token=token)
        # Send an invalid command
        self.assertJSON(self.post(url, params.replace(smsAddressAction='')), 0)
        self.assertJSON(self.post(url, params.replace(smsAddressAction='xxx')), 0)

    def test_move(self):
        'Make sure that only superusers can promote or demote other users'
        url = self.get_url('user_move')
        # Check that we only see the login page if the user is not logged in
        self.assert_('value=Login' in self.post(url).unicode_body)
        # Check that normal users can't promote or demote other users
        self.login(self.userN)
        token = get_token(self.get(self.get_url('user_index')).body)
        targetUser = db.query(User).filter_by(username=self.userS['username']).first()
        params = ReplaceableDict(token=token, targetUserID=targetUser.id, is_super=1)
        self.assert_('value=Login' in self.post(url, params.replace(is_super=0)))
        self.assert_('value=Login' in self.post(url, params.replace(is_super=1)))
        # Prepare
        self.login(self.userS)
        user = db.query(User).filter_by(username=self.userS['username']).first()
        token = get_token(self.get(self.get_url('user_index')).body)
        targetUser = db.query(User).filter_by(username=self.userN['username']).first()
        params = ReplaceableDict(token=token, targetUserID=targetUser.id, is_super=1)
        # Check that a bad token fails
        self.assertJSON(self.post(url, params.replace(token=token + 'x')), 0)
        # Check that a bad targetUserID fails
        self.assertJSON(self.post(url, params.replace(targetUserID=0)), 0)
        # Check that a bad is_super fails
        self.assertJSON(self.post(url, params.replace(is_super='xxx')), 0)
        # Check that a super user cannot promote or demote self
        self.assertJSON(self.post(url, params.replace(targetUserID=user.id, is_super=0)), 0)
        self.assertJSON(self.post(url, params.replace(targetUserID=user.id, is_super=1)), 0)
        # Check that a super user can promote or demote other users
        self.assertJSON(self.post(url, params.replace(is_super=1)), 1)
        self.assertJSON(self.post(url, params.replace(is_super=0)), 1)

    def test_reset(self):
        'Make sure that resetting the password works'
        url = self.get_url('user_reset')
        email = self.userN['email']
        password_ = hash(self.userN['password'])
        # Trying to reset an email that does not exist returns an error
        self.assertJSON(self.post(url, dict(email=email + 'x')), 0)
        # Resetting the password does not immediately change the password
        self.assertJSON(self.post(url, dict(email=email)), 1)
        self.assertEqual(db.query(User).filter_by(email=email, password_=password_).count(), 1)
        # Apply change
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(email=email, password_=password_).count(), 0)
