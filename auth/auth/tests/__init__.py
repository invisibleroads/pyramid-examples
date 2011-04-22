'Test templates'
import os
import webtest
import shutil
import unittest
import tempfile
import simplejson
import transaction
from ConfigParser import ConfigParser

from auth import main
from auth.models import DBSession, User
from auth.libraries.tools import hash_string


temporaryFolder = tempfile.mkdtemp()


class TestTemplate(unittest.TestCase):

    router = main({}, **{
        'sqlalchemy.url': 'sqlite://',
        'mail.queue_path': os.path.join(temporaryFolder, 'mail'),
        'mail.default_sender': 'auth <support@example.com>',
    })

    def setUp(self):
        db = DBSession()
        # Initialize functional test framework
        self.app = webtest.TestApp(self.router)
        self.logout()
        if not os.path.exists(temporaryFolder):
            os.mkdir(temporaryFolder)
        # Reset users
        self.userS = {'username': 'super', 'password': 'passwordS', 'nickname': u'SuperSuper', 'email': 'super@example.com'}
        self.userN = {'username': 'normal', 'password': 'passwordN', 'nickname': u'NormalUser', 'email': 'normal@example.com'}
        for userIndex, valueByKey in enumerate([self.userS, self.userN], 1):
            username, password, nickname, email = [valueByKey.get(x) for x in 'username', 'password', 'nickname', 'email']
            db.merge(User(id=userIndex, username=username, password_hash=hash_string(password), nickname=nickname, email=email, is_super=userIndex % 2))
        transaction.commit()

    def tearDown(self):
        shutil.rmtree(temporaryFolder)

    def get_url(self, name, **kw):
        'Return URL for route'
        return self.router.routes_mapper.generate(name, kw)

    def login(self, userD):
        'Login using credentials'
        return self.app.post(self.get_url('user_login'), userD)

    def logout(self):
        'Logout'
        return self.app.post(self.get_url('user_logout'))

    def assertJSON(self, response, isOk):
        'Assert response JSON'
        responseData = simplejson.loads(response.body)
        if responseData['isOk'] != isOk:
            print responseData
        self.assertEqual(responseData['isOk'], isOk)
        return responseData
