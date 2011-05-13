# -*- coding: utf-8 -*-
'Test templates'
import os; basePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import webtest
import shutil
import unittest
import simplejson
import transaction
import warnings; warnings.simplefilter('error')

from auth import main, load_settings
from auth.models import db, User


configurationPath = os.path.join(basePath, 'test.ini')
settings = load_settings(configurationPath, basePath)


class TestTemplate(unittest.TestCase):

    router = main({'__file__': configurationPath}, **settings)

    def setUp(self):
        # Initialize functional test framework
        self.app = webtest.TestApp(self.router)
        self.logout()
        # Reset users
        word = 'Спасибо'.decode('utf-8')
        self.userS = ReplaceableDict() # Super
        self.userA = ReplaceableDict() # Active
        self.userI = ReplaceableDict() # Inactive
        for userID, valueByKey in enumerate([self.userS, self.userA, self.userI], 1):
            wordNumber = word + str(userID)
            valueByKey['username'] = wordNumber
            valueByKey['password'] = wordNumber
            valueByKey['nickname'] = wordNumber
            valueByKey['email'] = wordNumber + '@example.com'
            valueByKey['is_active'] = userID != 3
            valueByKey['is_super'] = userID == 1
            user = User(
                id=userID, 
                username=valueByKey['username'], 
                password=valueByKey['password'],
                nickname=valueByKey['nickname'],
                email=valueByKey['email'],
                is_active=valueByKey['is_active'],
                is_super=valueByKey['is_super'])
            db.merge(user)
        transaction.commit()

    def get_url(self, name, **kwargs):
        'Return URL for route'
        return self.router.routes_mapper.generate(name, kwargs)

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

    def assert_json(self, response, isOk):
        'Assert response JSON'
        data = simplejson.loads(response.unicode_body)
        if data['isOk'] != isOk:
            print data
        self.assertEqual(data['isOk'], isOk)
        return data

    def assert_forbidden(self, url, isForbidden=True, method='GET'):
        'Return True if the page is forbidden'
        body = getattr(self, method.lower())(url).body
        return self.assertEqual('value=Login' in body, isForbidden)


def unicode_dictionary(dictionary):
    'Convert the values of the dictionary to unicode'
    if not dictionary:
        return {}
    return dict((key, value.encode('utf-8') if isinstance(value, unicode) else value) for key, value in dictionary.iteritems())


def get_token(body):
    match = re.search("token = '(.*)'", body)
    return match.group(1) if match else ''


class ReplaceableDict(dict):
    
    def replace(self, **kwargs):
        return ReplaceableDict(self.items() + kwargs.items())
