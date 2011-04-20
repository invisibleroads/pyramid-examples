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
from auth.models import db, User
from auth.libraries.tools import hash_string


temporaryFolder = tempfile.mkdtemp()


class TestTemplate(unittest.TestCase):

    router = main({}, **{
        'sqlalchemy.url': 'sqlite://',
        'mail.queue_path': os.path.join(temporaryFolder, 'mail'),
        'mail.default_sender': 'auth <support@example.com>',
    })

    def setUp(self):
        self.app = webtest.TestApp(self.router)
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
        self.logout()
        if not os.path.exists(temporaryFolder):
            os.mkdir(temporaryFolder)

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
        self.assertEqual(responseData['isOk'], isOk)
        return responseData
