'Page access tests'
from auth.tests import TestTemplate


class TestPageAccess(TestTemplate):

    def test_public(self):
        'Make sure the public page is visible without authentication'
        url = self.get_url('page_public')
        # Make sure the view is visible to the public
        self.get(url)

    def test_protected(self):
        'Make sure the protected page is visible only after authentication'
        url = self.get_url('page_protected')
        # Make sure the view is not visible to the public
        self.assert_('value=Login' in self.get(url).unicode_body)
        # Make sure the view is visible to normal users
        self.login(self.userN)
        self.get(url)

    def test_privileged(self):
        'Make sure the protected page is visible only to super users'
        url = self.get_url('page_privileged')
        # Make sure the view is not visible to the public
        self.assert_('value=Login' in self.get(url).unicode_body)
        # Make sure the view is not visible to normal users
        self.assert_('value=Login' in self.get(url).unicode_body)
        # Make sure the view is visible to super users
        self.login(self.userS)
        self.get(url)
