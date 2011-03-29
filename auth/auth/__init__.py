"""Pyramid WSGI configuration"""
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Everyone, Authenticated
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import base64

from auth.models import initialize_sql
from auth.libraries.tools import make_random_string


def main(global_config, **settings):
    """Return a Pyramid WSGI application"""
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
        settings=settings, 
        authentication_policy=authenticationPolicy,
        authorization_policy=ACLAuthorizationPolicy(),
        renderer_globals_factory=make_renderer_globals,
        root_factory='auth.RootFactory')
    # Configure routes and views
    config.add_route('index', '/',
        view='auth.views.index', 
        view_renderer='index.mak')
    config.add_route('login', '/login', 
        view='auth.views.login',
        view_renderer='login.mak')
    config.add_route('logout', '/logout', 
        view='auth.views.logout')
    config.add_route('public', '/public', 
        view='auth.views.public',
        view_renderer='page.mak',
        permission='public')
    config.add_route('protected', '/protected', 
        view='auth.views.protected',
        view_renderer='page.mak',
        permission='protected')
    config.add_route('privileged', '/privileged', 
        view='auth.views.privileged',
        view_renderer='page.mak',
        permission='privileged')
    config.add_view('auth.views.login',
        renderer='login.mak',
        context='pyramid.exceptions.Forbidden')
    # Return WSGI app
    return config.make_wsgi_app()


class RootFactory(object):

    __acl__ = [ 
        (Allow, Everyone, 'public'),
        (Allow, Authenticated, 'protected'),
        (Allow, 'super', 'privileged'),
    ]

    def __init__(self, request):
        pass


def format_tokens(user):
    """Convert unicode so that it can be stored in a cookie"""
    return ['x' + base64.urlsafe_b64encode(user.nickname.encode('utf8')).replace('=', '+')] + user.get_groups()


def parse_tokens(tokens):
    nickname = base64.urlsafe_b64decode(tokens[0][1:].replace('+', '=')).decode('utf8')
    return nickname, tokens[1:]
