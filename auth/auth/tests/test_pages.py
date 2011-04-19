'Page access tests'
import unittest
import webtest
from pyramid.exceptions import Forbidden


from auth import main


class TestPageAccess(unittest.TestCase):

    def test_public(self):
        url = '/'
        # Make sure the view is visible to the public
        app.get(url)

    def test_protected(self):
        url = '/protected'
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, app.get, url)
        # Make sure the view is visible to normal users
        # 
        app.get(url)

    def test_privileged(self):
        url = '/privileged'
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, app.get, url)
        # Make sure the view is not visible to normal users
        # 
        self.assertRaises(Forbidden, app.get, url)
        # Make sure the view is visible to super users
        # 
        app.get(url)


app = webtest.TestApp(main({}, **{'sqlalchemy.url': 'sqlite://'}))
