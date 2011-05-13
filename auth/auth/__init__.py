'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ALL_PERMISSIONS, Allow, Authenticated, Deny, authenticated_userid
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from sqlalchemy import engine_from_config
from sqlalchemy.pool import QueuePool, NullPool
import logging; log = logging.getLogger(__name__)
import ConfigParser
import os

from auth.libraries import tools
from auth.models import initialize_sql
from auth.views import users, pages
from auth.parameters import *


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    settings.update({ 
        'mako.default_filters': 'h',
        'mako.directories': 'auth:templates',
        'cache.regions': 'short, medium, long',
    })
    # Load sensitive configuration
    if '__file__' in global_config:
        settings.update(load_sensitive_settings(global_config['__file__'], global_config))
    if 'ciphers.secret' in settings:
        tools.secret = settings['ciphers.secret']
    # Connect to database
    sqlalchemyURL = settings['sqlalchemy.url'].strip()
    initialize_sql(engine_from_config(settings, 'sqlalchemy.', 
        poolclass=NullPool if sqlalchemyURL.startswith('sqlite:///') else QueuePool))
    # Define methods
    def get_groups(userID, request):
        'Return access categories associated with the user'
        # Get properties
        properties = users.get_properties(userID)
        if not properties:
            return []
        is_active, is_super, code = properties[-3:]
        # Check code
        identity = authenticationPolicy.cookie.identify(request)
        if code != users.parse_tokens(identity['tokens'])[0]:
            return ['d']
        # Set groups
        groups = []
        if is_active:
            groups.append('a')
        if is_super:
            groups.append('s')
        return groups
    def make_renderer_globals(system):
        'Define template constants'
        userID = authenticated_userid(system['request'])
        properties = users.get_properties(userID) or (u'', MINUTES_OFFSET, False, False, '')
        nickname, minutes_offset, is_active, is_super = properties[:-1]
        return dict(
            SITE_NAME=SITE_NAME, 
            SITE_VERSION=SITE_VERSION, 
            USER_ID=userID, 
            USER_NICKNAME=nickname, 
            USER_OFFSET=minutes_offset, 
            IS_SUPER=is_super, 
            IS_ACTIVE=is_active)
    # Prepare configuration
    if not settings.get('authtkt.secret'):
        settings['authtkt.secret'] = os.urandom(SECRET_LEN)
    authenticationPolicy = AuthTktAuthenticationPolicy(settings['authtkt.secret'], 
        callback=get_groups, http_only=True)
    config = Configurator(
        settings=settings,
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='active',
        renderer_globals_factory=make_renderer_globals,
        root_factory='auth.RootFactory')
    # Configure transaction manager and mailer
    config.include('pyramid_tm')
    config.include('pyramid_mailer')
    # Configure sessions and caching
    if not settings.get('session.secret'):
        settings['session.secret'] = os.urandom(SECRET_LEN)
    config.set_session_factory(session_factory_from_settings(settings))
    set_cache_regions_from_settings(settings)
    # Configure static assets
    config.add_static_view('static', 'auth:static')
    # Configure routes for user account management
    config.include(users)
    # Configure routes that demonstrate access control
    config.include(pages)
    # Return WSGI app
    return config.make_wsgi_app()


def load_settings(configurationPath, basePath):
    'Load settings'
    defaultByKey = {'here': basePath}
    configParser = ConfigParser.ConfigParser(defaultByKey)
    if not configParser.read(configurationPath):
        raise ConfigParser.Error('Could not open %s' % configurationPath)
    settings = {}
    for key, value in configParser.items('app:auth'):
        if 'use' == key:
            if value.startswith('config:'):
                settings.update(load_settings(value.replace('config:', ''), basePath))
        settings[key] = value
    settings.update(load_sensitive_settings(configurationPath, defaultByKey))
    return settings


def load_sensitive_settings(configurationPath, defaultByKey):
    'Load sensitive settings from hidden configuration file'
    configFolder, configName = os.path.split(configurationPath)
    sensitivePath = os.path.join(configFolder, '.' + configName)
    settings = {}
    configParser  = ConfigParser.ConfigParser(defaultByKey)
    if not configParser.read(sensitivePath):
        log.warn('Could not open %s' % sensitivePath)
        return settings
    for section in configParser.sections():
        settings.update(configParser.items(section))
    return settings


class RootFactory(object):
    'Permission definitions'
    __acl__ = [ 
        (Deny, 'd', ALL_PERMISSIONS),
        (Allow, 's', 'super'),
        (Allow, 'a', 'active'),
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        pass
