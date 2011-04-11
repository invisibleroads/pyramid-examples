'Pyramid WSGI configuration'
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings

from board.models import initialize_sql
from board import views


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Connect to database
    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))
    # Define methods
    def make_renderer_globals(system):
        'Define template constants'
        return {'SITE_NAME': 'Board'}
    # Prepare configuration
    config = Configurator(settings=settings, 
        renderer_globals_factory=make_renderer_globals)
    # Configure caching
    set_cache_regions_from_settings(settings)
    # Configure static assets
    config.add_static_view('static', 'board:static')
    # Configure routes
    config.scan(views)
    config.include(views.add_routes)
    # Return WSGI app
    return config.make_wsgi_app()
