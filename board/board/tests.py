'Tests'
import unittest
from pyramid.config import Configurator
from pyramid import testing
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import create_engine

from board.models import DBSession, Post, initialize_sql


initialize_sql(create_engine('sqlite://'))


class TestViews(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        set_cache_regions_from_settings({
            'cache.type': 'memory',
            'cache.regions': 'minute',
        })

    def tearDown(self):
        testing.tearDown()

    def test_index(self):
        from board.views import index
        db = DBSession()
        # Make sure that index() returns as many posts as exist in the database
        info = index(testing.DummyRequest())
        self.assertEqual(len(info['posts']), db.query(Post).count())

    def test_index_(self):
        from board.views import index_
        db = DBSession()
        # Make sure that index_() does not add empty posts
        postCount = db.query(Post).count()
        info = index_(testing.DummyRequest(params={'text': u''}, post=True))
        self.assertEqual(len(info['posts']), postCount)
        # Make sure that index_() increments the number of posts
        postCount = db.query(Post).count()
        info = index_(testing.DummyRequest(params={'text': u'four'}, post=True))
        self.assertEqual(len(info['posts']), postCount + 1)

    def test_debug(self):
        from board.views import debug
        # Make sure that debug() raises an exception
        self.assertRaises(Exception, debug, testing.DummyRequest())
