'Pyramid WSGI configuration'
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from auth.models import initialize_sql
from auth.views import pages
from auth.parameters import *


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Connect to database
    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))
    # Define methods
    def make_renderer_globals(system):
        'Define template constants'
        # identity = authenticationPolicy.cookie.identify(system['request'])
        # if identity:
            # userID = identity['userid']
            # userNickname, userGroups = parse_tokens(identity['tokens'])
        # else:
        userID = None
        userNickname, userGroups = u'', []
        return dict(
            SITE_NAME=SITE_NAME, 
            SITE_VERSION=SITE_VERSION,
            USER_ID=userID,
            USER_GROUPS=userGroups,
            USER_NICKNAME=userNickname)
    # Prepare configuration
    config = Configurator(settings=settings,
        renderer_globals_factory=make_renderer_globals)
    # Configure static assets
    config.add_static_view('static', 'auth:static')
    # Configure routes that demonstrate access control
    config.scan(pages)
    config.include(pages.add_routes)
    # Return WSGI app
    return config.make_wsgi_app()
