'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from ConfigParser import ConfigParser
import os

from auth.libraries.tools import make_random_string
from auth.models import initialize_sql
from auth.views import pages
from auth.parameters import *


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
            userNickname, userGroups = parse_tokens(identity['tokens'])
        else:
            userID = None
            userNickname, userGroups = u'', []
        return dict(
            SITE_NAME=SITE_NAME, 
            SITE_VERSION=SITE_VERSION,
            USER_ID=userID,
            USER_NICKNAME=userNickname,
            USER_GROUPS=userGroups)
    # Load sensitive configuration
    configFolder, configName = os.path.split(global_config['__file__'])
    configParser = ConfigParser(global_config)
    if configParser.read(os.path.join(configFolder, '.' + configName)):
        settings.update(configParser.items('app:auth'))
    # Prepare configuration
    if 'authtkt.secret' not in settings:
        settings['authtkt.secret'] = make_random_string(SECRET_LEN)
    authenticationPolicy = AuthTktAuthenticationPolicy(settings['authtkt.secret'], callback=get_groups, http_only=True)
    config = Configurator(
        settings=settings,
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='protected',
        renderer_globals_factory=make_renderer_globals,
        root_factory='auth.RootFactory')
    # Configure transaction manager
    config.include('pyramid_tm')
    # Configure static assets
    config.add_static_view('static', 'auth:static')
    # Configure routes that demonstrate access control
    config.scan(pages)
    config.include(pages.add_routes)
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
