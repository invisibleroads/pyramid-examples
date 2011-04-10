'Pyramid WSGI configuration'
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
import pyramid_beaker

from board.models import initialize_sql
from board.libraries.tools import make_random_string


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Connect to database
    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))
    # Define methods
    def make_renderer_globals(system):
        'Define template constants'
        return {
            'SITE_NAME': 'Board',
        }
    # Prepare configuration
    config = Configurator(settings=settings, renderer_globals_factory=make_renderer_globals)
    # Configure sessions and caching
    settings['session.secret'] = make_random_string(32)
    config.set_session_factory(pyramid_beaker.session_factory_from_settings(settings))
    pyramid_beaker.set_cache_regions_from_settings(settings)
    # Configure routes
    config.add_static_view('static', 'board:static')
    config.add_route('index', '/', view='board.views.index', view_renderer='index.mak', request_method='GET')
    config.add_route('add', '/', view='board.views.add', view_renderer='index_.mak', request_method='POST')
    # Return WSGI app
    return config.make_wsgi_app()
