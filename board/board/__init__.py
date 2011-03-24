"""Pyramid WSGI configuration"""
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings

from board.models import initialize_sql


def main(global_config, **settings):
    """Return a Pyramid WSGI application"""
    # Connect to database
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    # Prepare configuration
    config = Configurator(settings=settings)
    # Configure sessions and caches
    config.set_session_factory(session_factory_from_settings(settings))
    set_cache_regions_from_settings(settings)
    # Configure routes
    config.add_static_view('static', 'board:static')
    config.add_route('index', '/', view='board.views.index',
        view_renderer='index.mak', request_method='GET')
    config.add_route('add', '/', view='board.views.add',
        view_renderer='index_.mak', request_method='POST')
    # Return WSGI app
    return config.make_wsgi_app()
