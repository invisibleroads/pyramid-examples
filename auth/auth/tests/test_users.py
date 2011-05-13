'Tests for user account management'
import imapIO
import unittest

from auth.views import users
from auth.libraries import sms
from auth.tests import settings
from auth.models import db, User, User_, SMSAddress
from auth.tests import TestTemplate, ReplaceableDict, get_token


class TestUsers(TestTemplate):

    def test_index(self):
        'Assert that the user index page shows how many accounts are on file'
        url = self.get_url('user_index')
        # Make sure that the user index page is visible
        self.assert_('%s users' % db.query(User).count() in self.get(url).unicode_body)

    def test_registration(self):
        'Make sure that registration works'
        url = self.get_url('user_register')
        username, password, nickname, email = [self.userS[x].replace('1', '9') for x in 'username', 'password', 'nickname', 'email']
        params = ReplaceableDict(username=username, password=password, nickname=nickname, email=email)
        # Make sure the registration page appears properly
        self.assert_('Registration' in self.get(url).unicode_body)
        # Register
        registrationCount1 = db.query(User_).count()
        self.post(url, params)
        # Register with a username that already exists
        self.assert_json(self.post(url, params.replace(username=self.userS['username'])), 0)
        # Register with a nickname that already exists
        self.assert_json(self.post(url, params.replace(nickname=self.userS['nickname'])), 0)
        # Register with a email that already exists
        self.assert_json(self.post(url, params.replace(email=self.userS['email'])), 0)
        # Register with a weak password
        self.assert_json(self.post(url, params.replace(password='xxx')), 0)
        # Register with the same username but with different case
        self.post(url, params.replace(username=username.upper(), nickname=nickname + 'x', email=email + 'x'))
        # Register with the same nickname but with different case
        self.post(url, params.replace(username=username + 'x', nickname=nickname.upper(), email=email + 'x'))
        # Register with the same email but with different case
        self.post(url, params.replace(username=username + 'x', nickname=nickname + 'x', email=email.upper()))
        # Confirm with an invalid ticket
        self.get(self.get_url('user_confirm', ticket='xxx'))
        # Confirm registration
        registrationCount2 = db.query(User_).count()
        self.assertEqual(registrationCount2 - registrationCount1, +4)
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        # Make sure the user exists
        self.assertEqual(db.query(User).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        registrationCount3 = db.query(User_).count()
        self.assertEqual(registrationCount3 - registrationCount2, -4)

    def test_login(self):
        'Make sure that login works'
        url = self.get_url('user_login')
        url_ = self.get_url('user_update')
        # Going to a forbidden page displays the login page
        self.assert_forbidden(url_)
        # Going directly to the login page stores the target url
        self.assert_(url_ in self.get(url, dict(url=url_)).unicode_body)
        # Bad credentials fail
        self.assert_json(self.login(self.userI.replace(username='')), 0)
        self.assert_json(self.login(self.userI.replace(password='')), 0)
        self.assert_json(self.login(self.userI.replace(password=self.userI['password'] + 'x')), 0)
        # Good credentials succeed
        self.assert_json(self.login(self.userI), 1)

    def test_logout(self):
        'Make sure that logout works'
        url = self.get_url('user_logout')
        url_ = self.get_url('user_index')
        # Logging out redirects whether the user is authenticated or not
        self.assertEqual(url_, self.get(url, dict(url=url_)).location)
        self.login(self.userI)
        self.assertEqual(url_, self.get(url, dict(url=url_)).location)

    def test_update(self):
        'Make sure that updating credentials works'
        url = self.get_url('user_update')
        # Check that we only see the login page if the user is not logged in
        self.assert_forbidden(url)
        self.assert_forbidden(url, method='POST')
        # Check that the update form is filled with the user's credentials
        self.login(self.userI)
        body = self.get(url).unicode_body
        self.assert_(self.userI['username'] in body)
        self.assert_(self.userI['nickname'] in body)
        self.assert_(self.userI['email'].lower() in body)
        token = get_token(body)
        # Updating credentials requires a token
        username, password, nickname, email = ['0' + self.userI[x] for x in 'username', 'password', 'nickname', 'email']
        params = ReplaceableDict(token=token, username=username, password=password, nickname=nickname, email=email)
        self.assert_json(self.post(url, params.replace(token='')), 0)
        self.assert_json(self.post(url, params), 1)
        # Make sure the credentials have not changed yet
        self.assertEqual(db.query(User).filter_by(username=username, nickname=nickname, email=email).count(), 0)
        # Make sure the credentials have changed after confirmation
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(username=username, nickname=nickname, email=email).first().check(password), True)

    @unittest.skipIf(not settings.get('sms.imap.host'), 'not configured')
    def test_update_smsAddress(self):
        'Make sure that updating smsAddresses works'
        url = self.get_url('user_update')
        db.query(SMSAddress).delete()
        userSID, userSCode, userSEmail = db.query(User.id, User.code, User.email).filter_by(username=self.userS['username']).first()
        userAID, userACode, userAEmail = db.query(User.id, User.code, User.email).filter_by(username=self.userA['username']).first()
        userIID, userICode, userIEmail = db.query(User.id, User.code, User.email).filter_by(username=self.userI['username']).first()

        imapServer = sms.connect(self.router.registry.settings)
        # Register an invalid email address
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userSID, userSCode), fromWhom=''))
        # Register using an invalid userID or userCode
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (-1, userSCode), fromWhom='sms_' + userSEmail))
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userSID, -1), fromWhom='sms_' + userSEmail))
        # Register three email addresses
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userSID, userSCode), fromWhom='sms_' + userSEmail))
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userAID, userACode), fromWhom='sms_' + userAEmail))
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userIID, userICode), fromWhom='sms_' + userIEmail))
        # Register an address that already exists for the given user
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (userSID, userSCode), fromWhom='sms_' + userSEmail))
        # Remove an email address
        imapServer.revive('inbox', imapIO.build_message(subject='%s-%s' % (0, 'xxx'), fromWhom='sms_' + userSEmail))
        # Process
        sms.process(self.router.registry.settings)
        # Make sure we only have two registered SMS address
        self.assertEqual(2, db.query(SMSAddress).count())
        smsAddressA = db.query(SMSAddress).filter_by(user_id=userAID).first()
        smsAddressI = db.query(SMSAddress).filter_by(user_id=userIID).first()

        # Get token
        self.login(self.userI)
        token = get_token(self.get(url).unicode_body)

        params = ReplaceableDict(token=token, smsAddressAction='activate', smsAddressID=smsAddressI.id)
        # Activate an smsAddress that doesn't belong to the user
        self.assert_json(self.post(url, params.replace(smsAddressID=smsAddressA.id)), 0)
        # Activate an smsAddress
        self.assert_json(self.post(url, params), 1)
        self.assertEqual(db.query(SMSAddress.is_active).filter_by(user_id=userIID).first()[0], True)

        params = ReplaceableDict(token=token, smsAddressAction='deactivate', smsAddressID=smsAddressI.id)
        # Deactivate an smsAddress that doesn't belong to the user
        self.assert_json(self.post(url, params.replace(smsAddressID=smsAddressA.id)), 0)
        # Deactivate an smsAddress
        self.assert_json(self.post(url, params), 1)
        self.assertEqual(db.query(SMSAddress.is_active).filter_by(user_id=userIID).first()[0], False)

        params = ReplaceableDict(token=token, smsAddressAction='remove', smsAddressID=smsAddressI.id)
        # Remove an smsAddress that doesn't belong to the user
        self.assert_json(self.post(url, params.replace(smsAddressID=smsAddressA.id)), 0)
        # Remove an smsAddress that does belong to the user
        self.assert_json(self.post(url, params), 1)
        self.assertEqual(db.query(SMSAddress).filter_by(id=smsAddressI.id).count(), 0)

        params = ReplaceableDict(token=token)
        # Send an invalid command
        self.assert_json(self.post(url, params.replace(smsAddressAction='')), 0)
        self.assert_json(self.post(url, params.replace(smsAddressAction='xxx')), 0)

    def test_move(self):
        'Make sure that only superusers can promote or demote other users'
        url = self.get_url('user_move')
        # Check that we only see the login page if the user is not logged in
        self.assert_forbidden(url, method='POST')
        # Check that only super users can promote or demote other users
        for userD in self.userA, self.userI:
            self.login(userD)
            self.assert_forbidden(url, method='POST')

        self.login(self.userS)
        userID = db.query(User.id).filter_by(username=self.userS['username']).first()[0]
        token = get_token(self.get(self.get_url('user_index')).body)
        get_targetUser = lambda: db.query(User).filter_by(username=self.userI['username']).first()
        targetUser = get_targetUser()
        params = ReplaceableDict(token=token, targetUserID=targetUser.id, is_super=1, is_active=1)
        # Check that a bad token fails
        self.assert_json(self.post(url, params.replace(token=token + 'x')), 0)
        # Check that a bad targetUserID fails
        self.assert_json(self.post(url, params.replace(targetUserID=0)), 0)
        # Check that a bad attribute fails
        self.assert_json(self.post(url, params.replace(is_super='xxx')), 0)
        self.assert_json(self.post(url, params.replace(is_active='xxx')), 0)
        # Check that a super user cannot promote or demote self
        self.assert_json(self.post(url, params.replace(targetUserID=userID)), 0)
        # Check that a super user can promote or demote other users
        self.assert_json(self.post(url, params.replace(is_super=1)), 1)
        targetUser = get_targetUser()
        self.assertEqual(targetUser.is_super, True)
        self.assert_json(self.post(url, params.replace(is_super=0)), 1)
        targetUser = get_targetUser()
        self.assertEqual(targetUser.is_super, False)
        self.assert_json(self.post(url, params.replace(is_active=1)), 1)
        targetUser = get_targetUser()
        self.assertEqual(targetUser.is_active, True)
        self.assert_json(self.post(url, params.replace(is_active=0)), 1)
        targetUser = get_targetUser()
        self.assertEqual(targetUser.is_active, False)

    def test_mutate(self):
        'Make sure that mutating the user works'
        url = self.get_url('user_mutate')
        self.login(self.userI)
        token = get_token(self.get(self.get_url('user_update')).body)
        params = ReplaceableDict(token=token)
        # Check that a bad token fails
        self.assert_json(self.post(url, params.replace(token=token + 'x')), 0)
        # Check that we can mutate the user code
        userCode = db.query(User.code).filter_by(username=self.userI['username']).first()[0]
        self.assert_json(self.post(url, params), 1)
        self.assertNotEqual(userCode, db.query(User.code).filter_by(username=self.userI['username']).first()[0])

    def test_reset(self):
        'Make sure that resetting the password works'
        url = self.get_url('user_reset')
        password, email = [self.userI[x] for x in 'password', 'email']
        # Trying to reset an email that does not exist returns an error
        self.assert_json(self.post(url, dict(email=email + 'x')), 0)
        # Resetting the password does not immediately change the password
        self.assert_json(self.post(url, dict(email=email)), 1)
        self.assertEqual(db.query(User).filter_by(email=email).first().check(password), True)
        # Apply change
        self.get(self.get_url('user_confirm', ticket=db.query(User_.ticket).filter_by(email=email).order_by(User_.when_expired.desc()).first()[0]))
        self.assertEqual(db.query(User).filter_by(email=email).first().check(password), False)
