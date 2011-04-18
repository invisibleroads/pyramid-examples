# fix login
# fix logout
# fix index
# fix register and register_
# fix confirm and confirm_
# fix update and update_
# fix datetime format for /users
# fix reset
# fix whenIO to use pytz and display timezone
# add salt to store in db
# consider overwriting AuthTktAuthenticationPolicy
# add CSRF to account update
'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from sqlalchemy import engine_from_config
from ConfigParser import ConfigParser
import os

from auth.libraries.tools import make_random_string
from auth.parameters import SITE_NAME, SITE_VERSION
from auth.models import initialize_sql
from auth.views import users


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Connect to database
    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))
    # Define methods
    def get_groups(userID, request):
        'Return a list of groups associated with the authenticated user'
        identity = authenticationPolicy.cookie.identify(request)
        if identity:
            return identity['tokens'][1:]
    def make_renderer_globals(system):
        'Define template constants'
        identity = authenticationPolicy.cookie.identify(system['request'])
        if identity:
            userID = identity['userid']
            nickname, groups = users.parse_tokens(identity['tokens'])
        else:
            userID = None
            nickname, groups = u'', []
        return {
            'SITE_NAME': SITE_NAME,
            'SITE_VERSION': SITE_VERSION,
            'USER_ID': userID,
            'USER_GROUPS': groups,
            'USER_NICKNAME': nickname,
        }
    # Load sensitive configuration
    configFolder, configName = os.path.split(global_config['__file__'])
    configParser = ConfigParser(global_config)
    configParser.read(os.path.join(configFolder, '.' + configName))
    settings.update(configParser.items('app:auth'))
    # Prepare configuration
    authenticationPolicy = AuthTktAuthenticationPolicy(make_random_string(32), 
        callback=get_groups, http_only=True)
    config = Configurator(settings=settings,
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='protected',
        renderer_globals_factory=make_renderer_globals,
        root_factory='auth.RootFactory')
    # Configure sessions and caching
    if 'session.secret' not in settings:
        settings['session.secret'] = make_random_string(32)
    config.set_session_factory(session_factory_from_settings(settings))
    set_cache_regions_from_settings(settings)
    # Configure mailer
    config.include('pyramid_mailer')
    # Configure static assets
    config.add_static_view('static', 'auth:static')
    # Configure routes for user account management
    config.scan(users)
    config.include(users.add_routes)
    # Configure routes
    config.add_route('public', '', view='auth.views.public', view_renderer='page.mak', permission='__no_permission_required__')
    config.add_route('protected', '/protected', view='auth.views.protected', view_renderer='page.mak', permission='protected')
    config.add_route('privileged', '/privileged', view='auth.views.privileged', view_renderer='page.mak', permission='privileged')
    # Return WSGI app
    return config.make_wsgi_app()


class RootFactory(object):
    'Permission definitions'
    __acl__ = [ 
        (Allow, Authenticated, 'protected'),
        (Allow, 'super', 'privileged'),
    ]

    def __init__(self, request):
        pass
