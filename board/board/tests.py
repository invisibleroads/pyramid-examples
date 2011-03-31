'Tests'
import unittest
from pyramid.config import Configurator
from pyramid import testing
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import create_engine

from board.models import initialize_sql, Post


class TestViews(unittest.TestCase):

    db = initialize_sql(create_engine('sqlite://'))

    def setUp(self):
        self.config = testing.setUp()
        set_cache_regions_from_settings({
            'cache.type': 'memory',
            'cache.regions': 'minute, hour',
        })

    def tearDown(self):
        testing.tearDown()

    def test_index(self):
        from board.views import index
        # Make sure that index() returns as many posts as exist in the database
        request = testing.DummyRequest()
        info = index(request)
        self.assertEqual(len(info['posts']), self.db.query(Post).count())

    def test_add(self):
        from board.views import add
        # Make sure that add() does not add empty posts
        postCount = self.db.query(Post).count()
        request = testing.DummyRequest(params={'text': u''}, post=True)
        info = add(request)
        self.assertEqual(len(info['posts']), postCount)
        # Make sure that add() increments the number of posts
        postCount = self.db.query(Post).count()
        request = testing.DummyRequest(params={'text': u'four'}, post=True)
        info = add(request)
        self.assertEqual(len(info['posts']), postCount + 1)
