'Views for user account management'
import datetime
from pyramid.view import view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from email.utils import formataddr
from formencode import validators, Schema, All, Invalid
from recaptcha.client import captcha
from sqlalchemy.orm import joinedload
from beaker.cache import cache_region, region_invalidate

from auth.models import db, User, User_, SMSAddress
from auth.libraries.tools import make_random_string, make_random_unique_string
from auth.parameters import *


def includeme(config):
    config.scan(__name__)
    config.add_route('user_index', 'users')
    config.add_route('user_register', 'users/register')
    config.add_route('user_confirm', 'users/confirm/{ticket}')
    config.add_route('user_login', 'users/login')
    config.add_route('user_logout', 'users/logout')
    config.add_route('user_update', 'users/update')
    config.add_route('user_move', 'users/move')
    config.add_route('user_mutate', 'users/mutate')
    config.add_route('user_reset', 'users/reset')


@view_config(route_name='user_index', renderer='users/index.mak', permission='__no_permission_required__')
def index(request):
    'Show information about people registered in the database'
    return dict(users=db.query(User).order_by(User.when_login.desc()).all())


@view_config(route_name='user_register', renderer='users/change.mak', request_method='GET', permission='__no_permission_required__')
def register(request):
    'Show account registration page'
    return dict(user=None)


@view_config(route_name='user_register', renderer='json', request_method='POST', permission='__no_permission_required__')
def register_(request):
    'Store proposed changes and send confirmation email'
    return save_user_(request, dict(request.params), 'registration')


@view_config(route_name='user_confirm', permission='__no_permission_required__')
def confirm(request):
    'Confirm changes'
    # Apply changes to user account
    try:
        user_ = apply_user_(request.matchdict.get('ticket', ''))
    except UserException:
        message = 'Ticket expired'
    else:
        message = 'Account updated' if user_.user_id else 'Account created'
        # Delete expired or similar user_
        db.execute(User_.__table__.delete().where(
            (User_.when_expired < datetime.datetime.utcnow()) | 
            (User_.username == user_.username) | 
            (User_.nickname == user_.nickname) | 
            (User_.email == user_.email)))
    # Save message in session
    request.session.flash(message)
    # Return
    return HTTPFound(location=request.route_path('user_login'))


@view_config(route_name='user_login', renderer='users/login.mak', request_method='GET', permission='__no_permission_required__')
@view_config(renderer='users/login.mak', context='pyramid.exceptions.Forbidden', permission='__no_permission_required__')
def login(request):
    'Show login form'
    # If the user accessed the login page directly,
    if request.path == request.route_path('user_login'):
        # Get the target url from the query string
        url = request.params.get('url', '/')
    # If the user tried to access a forbidden resource,
    else:
        # Get the target url directly
        url = request.url
    # Return
    return dict(url=url, REJECTION_LIMIT=REJECTION_LIMIT)


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
    if not user.check(password):
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
        user.minutes_offset = int(params.get('minutes_offset', MINUTES_OFFSET))
    except ValueError:
        user.minutes_offset = MINUTES_OFFSET
    user.when_login = datetime.datetime.utcnow()
    user.rejection_count = 0
    # Set cookie
    if not hasattr(request, 'response_headerlist'):
        request.response_headerlist = []
    request.response_headerlist.extend(remember(request, user.id, tokens=format_tokens(user)))
    # Return
    return dict(isOk=1)


@view_config(route_name='user_logout', permission='__no_permission_required__')
def logout(request):
    'Logout'
    return HTTPFound(location=request.params.get('url', '/'), headers=forget(request))


@view_config(route_name='user_update', renderer='users/change.mak', request_method='GET', permission='authenticated')
def update(request):
    'Show account update page'
    userID = authenticated_userid(request)
    user = db.query(User).options(joinedload(User.sms_addresses)).get(userID)
    return dict(user=user)


@view_config(route_name='user_update', renderer='json', request_method='POST', permission='authenticated')
def update_(request):
    'Update account'
    params = request.params
    if params.get('token') != request.session.get_csrf_token():
        return dict(isOk=0, message='Invalid session token')
    userID = authenticated_userid(request)
    # If the user is trying to update account information, send confirmation email
    if 'username' in params:
        return save_user_(request, dict(params), 'update', db.query(User).get(userID))
    # Make sure the smsAddressID belongs to the user
    smsAddressID = params.get('smsAddressID')
    smsAddress = db.query(SMSAddress).filter(
        (SMSAddress.id == smsAddressID) & 
        (SMSAddress.user_id == userID)).first()
    if not smsAddress:
        return dict(isOk=0, message='Could not find smsAddressID=%s corresponding to userID=%s' % (smsAddressID, userID))
    # Load
    smsAddressAction = params.get('smsAddressAction')
    # If the user is activating an SMS address,
    if 'activate' == smsAddressAction:
        smsAddress.is_active = True
        return dict(isOk=1, is_active=smsAddress.is_active)
    # If the user is deactivating an SMS address,
    if 'deactivate' == smsAddressAction:
        smsAddress.is_active = False
        return dict(isOk=1, is_active=smsAddress.is_active)
    # If the user is removing an SMS address,
    elif 'remove' == smsAddressAction:
        db.delete(smsAddress)
        return dict(isOk=1)
    # If the command is not recognized,
    return dict(isOk=0, message='Command not recognized')


@view_config(route_name='user_move', renderer='json', request_method='POST', permission='super')
def move(request):
    'Move a user to a different access category'
    params = request.params
    if params.get('token') != request.session.get_csrf_token():
        return dict(isOk=0, message='Invalid session token')
    userID = authenticated_userid(request)
    # Load targetUser
    targetUserID = params.get('targetUserID', 0)
    targetUser = db.query(User).get(targetUserID)
    if not targetUser:
        return dict(isOk=0, message='Could not find targetUserID=%s' % targetUserID)
    if int(userID) == int(targetUserID):
        return dict(isOk=0, message='Cannot promote or demote yourself')
    # Load attributes
    hasAttributes = False
    for attributeName in 'is_active', 'is_super':
        value = params.get(attributeName)
        if value is None:
            continue
        try:
            value = bool(int(value))
        except ValueError:
            return dict(isOk=0, message='Could not parse %s=%s' % (attributeName, value))
        setattr(targetUser, attributeName, value)
        hasAttributes = True
    if not hasAttributes:
        return dict(isOk=0, message='No attributes specified')
    # Return
    region_invalidate(get_properties, None, targetUserID)
    return dict(isOk=1)


@view_config(route_name='user_mutate', renderer='json', request_method='POST', permission='authenticated')
def mutate(request):
    'Mutate user token'
    params = request.params
    if params.get('token') != request.session.get_csrf_token():
        return dict(isOk=0, message='Invalid session token')
    userID = authenticated_userid(request)
    # Mutate user code 
    user = db.query(User).get(userID)
    user.code = make_random_string(CODE_LEN)
    # Refresh cookie
    if not hasattr(request, 'response_headerlist'):
        request.response_headerlist = []
    request.response_headerlist.extend(remember(request, user.id, tokens=format_tokens(user)))
    # Return
    region_invalidate(get_properties, None, userID)
    return dict(isOk=1, code=user.code)


@view_config(route_name='user_reset', renderer='json', request_method='POST', permission='__no_permission_required__')
def reset(request):
    'Reset password'
    # Get email
    email = request.params.get('email')
    # Try to load the user
    user = db.query(User).filter(User.email==email).first()
    # If the email is not in our database,
    if not user: 
        return dict(isOk=0)
    # Reset account
    return save_user_(request, dict(
        username=user.username, 
        password=make_random_string(PASSWORD_LEN_MAX),
        nickname=user.nickname,
        email=user.email), 'reset', user)


def format_tokens(user):
    'Format user information into a cookie'
    code = 'x' + str(user.code)
    return [code]


def parse_tokens(tokens):
    'Parse user information from a cookie'
    code = tokens[0][1:]
    return [code]


@cache_region('medium')
def get_properties(userID):
    'Return user properties'
    return db.query(User.nickname, User.minutes_offset, User.is_active, User.is_super, User.code).filter_by(id=userID).first()


def save_user_(request, valueByName, action, user=None):
    'Validate values and send confirmation email if values are okay'
    # Validate form
    try:
        form = UserForm().to_python(valueByName, user)
    except Invalid, error:
        return dict(isOk=0, errorByID=error.unpack_errors())
    # Prepare ticket
    try:
        ticket = make_random_unique_string(TICKET_LEN, 
            lambda x: db.query(User_).filter_by(ticket=x).first() == None)
    except RuntimeError:
        return dict(isOk=0, errorByID={'status': 'Could not generate ticket; please try again later'})
    # Prepare user_
    user_ = User_(
        username=form['username'],
        password=form['password'], 
        nickname=form['nickname'], 
        email=form['email'],
        user_id=user.id if user else None,
        ticket=ticket,
        when_expired=datetime.datetime.utcnow() + datetime.timedelta(hours=TICKET_HOURS))
    db.add(user_)
    # Send message
    get_mailer(request).send_to_queue(Message(
        recipients=[formataddr((user_.nickname, user_.email))],
        subject='Confirm {}'.format(action),
        body=render('users/confirm.mak', {
            'form': form,
            'ticket': ticket,
            'action': action,
            'TICKET_HOURS': TICKET_HOURS,
        }, request)))
    # Return
    return dict(isOk=1)


def apply_user_(ticket):
    'Finalize a change to a user account'
    user_ = db.query(User_).filter(
        (User_.ticket == ticket) & 
        (User_.when_expired >= datetime.datetime.utcnow())).first()
    if not user_:
        raise UserException('')
    # If the ticket is valid,
    if user_:
        # Apply the change and reset rejection_count
        userID = user_.user_id
        db.merge(User(
            id=userID,
            username=user_.username,
            password_=user_.password_,
            nickname=user_.nickname,
            email=user_.email,
            rejection_count=0,
            code=make_random_string(CODE_LEN)))
        region_invalidate(get_properties, None, userID)
    # Return
    return user_


class Unique(validators.FancyValidator):
    'Validator to ensure that the value of a field is unique'

    def __init__(self, fieldName, errorMessage):
        'Store fieldName and errorMessage'
        super(Unique, self).__init__()
        self.fieldName = fieldName
        self.errorMessage = errorMessage

    def _to_python(self, value, user):
        'Check whether the value is unique'
        # If the user is new or the value changed,
        if not user or getattr(user, self.fieldName) != value:
            # Make sure the value is unique
            if db.query(User).filter(getattr(User, self.fieldName)==value).first():
                # Raise
                raise Invalid(self.errorMessage, value, user)
        # Return
        return value


class SecurePassword(validators.FancyValidator):
    'Validator to prevent weak passwords'

    def _to_python(self, value, user):
        'Check whether a password is strong enough'
        if len(set(value)) < 6:
            raise Invalid('That password needs more variety', value, user)
        return value


class UserForm(Schema):
    'User account validator'

    allow_extra_fields = True
    filter_extra_fields = True

    username = All(
        validators.UnicodeString(
            min=USERNAME_LEN_MIN,
            max=USERNAME_LEN_MAX,
            not_empty=True,
            strip=True),
        Unique('username', 'That username already exists'))
    password = All(
        validators.UnicodeString(
            min=PASSWORD_LEN_MIN,
            not_empty=True),
        SecurePassword())
    nickname = All(
        validators.UnicodeString(
            min=NICKNAME_LEN_MIN,
            max=NICKNAME_LEN_MAX,
            not_empty=True,
            strip=True),
        Unique('nickname', 'That nickname already exists'))
    email = All(
        validators.UnicodeString(
            max=EMAIL_LEN_MAX,
            not_empty=True,
            strip=True),
        validators.Email(),
        Unique('email', 'That email is reserved for another account'))


class UserException(Exception):
    pass
