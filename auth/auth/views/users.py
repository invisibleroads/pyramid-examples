'Views for user account management'
import base64
import datetime
from pyramid.view import view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound
from recaptcha.client import captcha

from auth.models import db, User, User_
from auth.libraries.tools import hash_string, make_random_string, make_random_unique_string
from auth.parameters import *


def includeme(config):
    config.add_route('user_index', 'users')
    config.add_route('user_register', 'users/register')
    config.add_route('user_confirm', 'users/confirm/{ticket}')
    config.add_route('user_login', 'users/login')
    config.add_route('user_logout', 'users/logout')
    config.add_route('user_update', 'users/update')
    config.add_route('user_reset', 'users/reset')


@view_config(route_name='user_index', renderer='users/index.mak', permission='__no_permission_required__')
def index(request):
    'Show information about people registered in the database'
    return dict(users=db.query(User).order_by(User.when_login.desc()).all())


@view_config(route_name='user_login', renderer='json', request_method='POST', permission='__no_permission_required__')
def login_(request):
    'Process login credentials'
    # Make shortcuts
    environ, params, registry = [getattr(request, x) for x in 'environ', 'params', 'registry']
    username, password = [params.get(x, '').strip() for x in 'username', 'password']
    if not username or not password:
        return dict(isOk=0)
    # Check username
    user = db.query(User).filter_by(username=username).first()
    if not user:
        return dict(isOk=0)
    # If the password is incorrect, increment and return rejection_count
    if user.password_hash != hash_string(password):
        user.rejection_count += 1
        return dict(isOk=0, rejection_count=user.rejection_count)
    # If there have been too many rejections, expect recaptcha
    if user.rejection_count >= REJECTION_LIMIT:
        rChallenge, rResponse = [params.get(x, '') for x in 'recaptcha_challenge', 'recaptcha_response']
        rPrivate = registry.settings.get('recaptcha.private', '')
        clientIP = environ.get('HTTP_X_REAL_IP', environ.get('HTTP_X_FORWARDED_FOR', environ.get('REMOTE_ADDR')))
        # If the response is not valid, say so
        if not captcha.submit(rChallenge, rResponse, rPrivate, clientIP).is_valid:
            return dict(isOk=0, rejection_count=user.rejection_count)
    # Save user
    try:
        user.offset = int(params.get('offset', MINUTES_OFFSET))
    except ValueError:
        user.offset = MINUTES_OFFSET
    user.when_login = datetime.datetime.utcnow()
    user.rejection_count = 0
    # Set headers to set cookie
    if not hasattr(request, 'response_headerlist'):
        request.response_headerlist = []
    request.response_headerlist.extend(remember(request, user.id, tokens=format_tokens(user)))
    # Return
    return dict(isOk=1)


@view_config(route_name='user_logout', permission='__no_permission_required__')
def logout(request):
    'Logout'
    return HTTPFound(location=request.params.get('url', '/'), headers=forget(request))


def format_tokens(user):
    'Format user information into a cookie'
    nickname = 'x' + base64.urlsafe_b64encode(user.nickname.encode('utf8')).replace('=', '+')
    offset = 'x' + str(user.offset)
    groups = user.groups
    return [nickname, offset] + groups


def parse_tokens(tokens):
    'Parse user information from a cookie'
    nickname = base64.urlsafe_b64decode(tokens[0][1:].replace('+', '=')).decode('utf8')
    offset = int(tokens[1][1:])
    groups = tokens[2:]
    return nickname, offset, groups
