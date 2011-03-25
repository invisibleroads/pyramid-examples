"""Pyramid WSGI configuration"""
from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from board.models import initialize_sql


def main(global_config, **settings):
    """Return a Pyramid WSGI application"""
    # Connect to database
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    # Prepare configuration
    config = Configurator(settings=settings)
    # Configure sessions and caches
    set_cache_regions_from_settings(settings)
    # Configure routes
    config.add_static_view('static', 'board:static')
    config.add_route('index', '/', request_method='GET',
        view='board.views.index',
        view_renderer='index.mak')
    config.add_route('add', '/', request_method='POST',
        view='board.views.add',
        view_renderer='index_.mak')
    # Return WSGI app
    return config.make_wsgi_app()
