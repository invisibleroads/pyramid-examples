# -*- coding: utf-8 -*-
'Test templates'
import os
import re
import webtest
import shutil
import unittest
import tempfile
import simplejson
import transaction
import warnings; warnings.simplefilter('error')
from ConfigParser import ConfigParser

from auth import main
from auth.models import db, User
from auth.libraries.tools import hash


temporaryFolder = tempfile.mkdtemp()


class TestTemplate(unittest.TestCase):

    router = main({}, **{
        'sqlalchemy.url': 'sqlite://',
        'mail.queue_path': os.path.join(temporaryFolder, 'mail'),
        'mail.default_sender': 'auth <support@example.com>',
    })

    def setUp(self):
        # Initialize functional test framework
        self.app = webtest.TestApp(self.router)
        self.logout()
        if not os.path.exists(temporaryFolder):
            os.mkdir(temporaryFolder)
        # Reset users
        word = 'Спасибо1'.decode('utf-8')
        self.userS = {'username': word, 'password': word, 'nickname': word, 'email': word + '@example.com'}
        self.userN = dict((key, value.replace('1', '2')) for key, value in self.userS.iteritems())
        for userIndex, valueByKey in enumerate([self.userS, self.userN], 1):
            username, password, nickname, email = [valueByKey.get(x) for x in 'username', 'password', 'nickname', 'email']
            db.merge(User(id=userIndex, username=username, password_=hash(password), nickname=nickname, email=email, is_super=userIndex % 2))
        transaction.commit()

    def tearDown(self):
        shutil.rmtree(temporaryFolder)

    def get_url(self, name, **kw):
        'Return URL for route'
        return self.router.routes_mapper.generate(name, kw)

    def get(self, url, params=None):
        'Send a GET request'
        return self.app.get(url, unicode_dictionary(params))

    def post(self, url, params=None):
        'Send a POST request'
        return self.app.post(url, unicode_dictionary(params))

    def login(self, userD):
        'Login using credentials'
        return self.post(self.get_url('user_login'), userD)

    def logout(self):
        'Logout'
        return self.post(self.get_url('user_logout'))

    def assertJSON(self, response, isOk):
        'Assert response JSON'
        data = simplejson.loads(response.unicode_body)
        if data['isOk'] != isOk:
            print data
        self.assertEqual(data['isOk'], isOk)
        return data


def unicode_dictionary(dictionary):
    'Convert the values of the dictionary to unicode'
    if not dictionary:
        return {}
    return dict((key, value.encode('utf-8') if isinstance(value, unicode) else value) for key, value in dictionary.iteritems())


def get_token(body):
    match = re.search("token = '(.*)'", body)
    return match.group(1) if match else ''


class ReplaceableDict(dict):
    
    def replace(self, **kw):
        return dict(self.items() + kw.items())
