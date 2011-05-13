'Page access tests'
from auth.tests import TestTemplate


class TestPageAccess(TestTemplate):

    def test_everyone(self):
        'Make sure the page is visible without authentication'
        url = self.get_url('page_everyone')
        # Make sure the view is visible without authentication
        self.assert_forbidden(url, False)
        # Make sure the view is visible with authentication
        for userD in self.userS, self.userA, self.userI:
            self.login(userD)
            self.assert_forbidden(url, False)

    def test_authenticated(self):
        'Make sure the page is visible only after authentication'
        url = self.get_url('page_authenticated')
        # Make sure the view is not visible without authentication
        self.assert_forbidden(url)
        # Make sure the view is visible with authentication
        for userD in self.userS, self.userA, self.userI:
            self.login(userD)
            self.assert_forbidden(url, False)

    def test_active(self):
        'Make sure the page is visible only after authentication'
        url = self.get_url('page_active')
        # Make sure the view is not visible to everyone
        self.assert_forbidden(url)
        # Make sure the view is only visible to active users
        for userD in self.userS, self.userA, self.userI:
            self.login(userD)
            self.assert_forbidden(url, not userD['is_active'])

    def test_super(self):
        'Make sure the page is visible only to super users'
        url = self.get_url('page_super')
        # Make sure the view is not visible to everyone
        self.assert_forbidden(url)
        # Make sure the view is only visible to super users
        for userD in self.userS, self.userA, self.userI:
            self.login(userD)
            self.assert_forbidden(url, not userD['is_super'])
