'Pyramid WSGI configuration'
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from auth.models import initialize_sql
from auth.libraries.tools import make_random_string
from auth.views import users, parse_tokens


def main(global_config, **settings):
    'Return a Pyramid WSGI application'
    # Connect to database
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    # Prepare configuration
    def get_groups(userID, request):
        identity = authenticationPolicy.cookie.identify(request)
        if identity:
            return identity['tokens'][1:]
    def make_renderer_globals(system):
        identity = authenticationPolicy.cookie.identify(system['request'])
        if identity:
            userID = identity['userid']
            nickname, groups = parse_tokens(identity['tokens'])
        else:
            userID = None
            nickname, groups = u'', []
        return {
            'SITE_NAME': 'Auth',
            'SITE_VERSION': '0.0',
            'USER_ID': userID,
            'USER_GROUPS': groups,
            'USER_NICKNAME': nickname,
        }
    authenticationPolicy = AuthTktAuthenticationPolicy(make_random_string(32), 
        callback=get_groups)
    config = Configurator(
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        default_permission='protected',
        renderer_globals_factory=make_renderer_globals,
        root_factory='auth.RootFactory',
        settings=settings)
    # Configure routes for user account management
    config.scan(users)
    config.include(users.add_routes)
    # Configure routes
    config.add_route('home', '',
        view='auth.views.home',
        view_renderer='home.mak')
    config.add_route('protected', '/protected', 
        view='auth.views.protected',
        view_renderer='page.mak',
        permission='protected')
    config.add_route('privileged', '/privileged', 
        view='auth.views.privileged',
        view_renderer='page.mak',
        permission='privileged')
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
