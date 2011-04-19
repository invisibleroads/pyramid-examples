'Views for user account management'
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from recaptcha.client import captcha
from formencode import validators, Schema, All, Invalid
from sqlalchemy.orm import joinedload
from email.utils import formataddr
import transaction
import base64
import datetime

from auth.models import db, User, User_
from auth.libraries.tools import hash_string, make_random_string, make_random_unique_string
from auth.parameters import *


def add_routes(config):
    config.add_route('user_index', 'users')
    config.add_route('user_register', 'users/register')
    config.add_route('user_confirm', 'users/confirm/{ticket}')
    config.add_route('user_login', 'users/login')
    config.add_route('user_update', 'users/update')
    config.add_route('user_logout', 'users/logout')
    config.add_route('user_reset', 'users/reset')


@view_config(route_name='user_index', renderer='users/index.mak', permission='__no_permission_required__')
def index(request):
    'Show information about people registered in the database'
    return dict(users=db.query(User).order_by(User.when_login.desc()).all())


@view_config(route_name='user_register', renderer='users/change.mak', request_method='GET', permission='__no_permission_required__')
def register(request):
    'Show account registration page'
    return dict(isNew=True, username='', nickname=u'', email='')


@view_config(route_name='user_register', renderer='json', request_method='POST', permission='__no_permission_required__')
def register_(request):
    'Store proposed changes and send confirmation email'
    return save_user_(request, dict(request.params), 'registration')


@view_config(route_name='user_confirm', permission='__no_permission_required__')
def confirm(request):
    'Confirm changes'
    # Apply changes to user account
    user_ = apply_user_(request.matchdict.get('ticket', ''))
    # If the user_ exists,
    if user_:
        # Set
        message = 'Account updated' if user_.user_id else 'Account created'
        # Delete expired or similar user_
        db.execute(User_.__table__.delete().where(
            (User_.when_expired < datetime.datetime.utcnow()) | 
            (User_.username == user_.username) | 
            (User_.nickname == user_.nickname) | 
            (User_.email == user_.email)))
        transaction.commit()
    # If the user_ does not exist,
    else:
        # Set
        message = 'Ticket expired'
    # Save flash in session
    request.session.flash(message)
    # Return
    return HTTPFound(location=request.route_url('user_login'))


@view_config(route_name='user_login', renderer='users/login.mak', request_method='GET', permission='__no_permission_required__')
@view_config(renderer='users/login.mak', context='pyramid.exceptions.Forbidden', permission='__no_permission_required__')
def login(request):
    'Show login form'
    # If the user accessed the login page directly,
    if request.url == request.route_url('user_login'):
        # Get the target url from the query string
        url = request.params.get('url', '/')
    # If the user tried to access a protected resource,
    else:
        # Get the target url directly
        url = request.url
    # Return
    return dict(url=url, REJECTION_LIMIT=REJECTION_LIMIT)


@view_config(route_name='user_login', renderer='json', request_method='POST', permission='__no_permission_required__')
def login_(request):
    'Process login credentials'
    # Define shortcuts
    environ, params, registry = [getattr(request, x) for x in 'environ', 'params', 'registry']
    # Check username
    user = db.query(User).filter_by(username=params.get('username', '')).first()
    # If the username does not exist,
    if not user:
        return dict(isOk=0)
    # If the password is incorrect,
    if user.password_hash != hash_string(params.get('password', '')):
        # Increase and return rejection_count
        rejection_count = user.rejection_count = user.rejection_count + 1
        transaction.commit()
        return dict(isOk=0, rejection_count=rejection_count)
    # If there have been too many rejections,
    if user.rejection_count >= REJECTION_LIMIT:
        # Expect recaptcha response
        recaptchaChallenge = params.get('recaptcha_challenge_field', '')
        recaptchaResponse = params.get('recaptcha_response_field', '')
        recaptchaPrivate = registry.settings.get('recaptcha.private', '')
        remoteIP = environ.get('HTTP_X_REAL_IP', 
                   environ.get('HTTP_X_FORWARDED_FOR', 
                   environ.get('REMOTE_ADDR')))
        # If the response is not valid,
        if not captcha.submit(recaptchaChallenge, recaptchaResponse, recaptchaPrivate, remoteIP).is_valid:
            return dict(isOk=0, rejection_count=user.rejection_count)
    # Save user
    user.when_login = datetime.datetime.utcnow()
    user.minutes_offset = get_minutes_offset()
    user.rejection_count = 0
    transaction.commit()
    # Save session
    session = request.session
    session['user.id'] = user.id
    session['user.groups'] = user.groups
    session['user.nickname'] = user.nickname
    session['user.minutes_offset'] = user.minutes_offset
    session.save()
    # Return
    return dict(isOk=1)


@view_config(route_name='user_update', renderer='users/change.mak', request_method='GET', permission='protected')
def update(request):
    'Show account update page'
    # Render
    user = db.query(User).options(joinedload(User.sms_addresses)).get(h.getUserID())
    c.isNew = False
    c.smsAddresses = user.sms_addresses
    # Return
    return htmlfill.render(render('/people/change.mak'), {
        'username': user.username,
        'nickname': user.nickname,
        'email': user.email,
    })


@view_config(route_name='user_update', renderer='json', request_method='POST', permission='protected')
def update_(request):
    'Update account'
    # Initialize
    userID = h.getUserID()
    # If the user is trying to update SMS information,
    if 'smsAddressID' in request.params:
        # Load
        action = request.params.get('action')
        smsAddressID = request.params['smsAddressID']
        smsAddress = db.query(SMSAddress).filter((SMSAddress.id==smsAddressID) & (SMSAddress.owner_id==userID)).first()
        if not smsAddress:
            return dict(isOk=0, message='Could not find smsAddressID=%s corresponding to userID=%s' % (smsAddressID, userID))
        # If the user is trying to activate an SMS address,
        elif action == 'activate':
            smsAddress.is_active = True
        # If the user is trying to deactivate an SMS address,
        elif action == 'deactivate':
            smsAddress.is_active = False
        # If the user is trying to remove an SMS address,
        elif action == 'remove':
            db.delete(smsAddress)
        # Otherwise,
        else:
            return dict(isOk=0, message='Command not recognized')
        # Commit and return
        db.commit()
        return dict(isOk=1)
    # If the user is trying to update account information,
    else:
        # Send update confirmation email
        return save_user_(request, dict(request.params), 'update', db.query(User).get(userID))


@view_config(route_name='user_logout', permission='__no_permission_required__')
def logout(request):
    headers = forget(request)
    # return HTTPFound(location=request.route_url('index'), headers=headers)
    'Logout'
    # If the user is logged in,
    if h.isUser():
        del session['user.minutes_offset']
        del session['user.id']
        del session['user.nickname']
        del session['user.type']
        session.save()
    # Redirect
    return redirect(request.params.get('url', '/'))


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
        password=make_random_string(PASSWORD_LENGTH), 
        nickname=user.nickname, 
        email=user.email
    ), 'reset', user)


def save_user_(request, valueByName, action, user=None):
    'Validate values and send confirmation email if values are okay'
    # Validate form
    try:
        form = UserForm().to_python(valueByName, user)
    except Invalid, error:
        return dict(isOk=0, errorByID=error.unpack_errors())
    # Prepare ticket
    try:
        ticket = make_random_unique_string(TICKET_LENGTH, 
            lambda x: db.query(User_).filter_by(ticket=x).first() == None)
    except RuntimeError:
        return dict(isOk=0, errorByID={
            'status': 'Could not generate ticket; please try again later'
        })
    # Prepare user_
    user_ = User_(
        username=form['username'],
        password_hash=hash_string(form['password']), 
        nickname=form['nickname'], 
        email=form['email'],
        user_id=user.id if user else None,
        ticket=ticket,
        when_expired=datetime.datetime.utcnow() + datetime.timedelta(hours=TICKET_LIFESPAN_IN_HOURS))
    db.add(user_)
    # Send message
    get_mailer(request).send_to_queue(Message(
        recipients=[
            formataddr((user_.nickname, user_.email)),
        ],
        subject='Confirm {}'.format(action),
        body=render('users/confirm.mak', {
            'form': form,
            'ticket': ticket,
            'action': action,
            'TICKET_LIFESPAN_IN_HOURS': TICKET_LIFESPAN_IN_HOURS,
        }, request)))
    transaction.commit()
    # Return
    return dict(isOk=1)


def apply_user_(ticket):
    'Finalize a change to a user account'
    # Load
    user_ = db.query(User_).filter(
        (User_.ticket == ticket) & 
        (User_.when_expired >= datetime.datetime.utcnow())).first()
    # If the ticket is valid,
    if user_:
        # Apply the change and reset rejection_count
        db.merge(User(
            id=user_.user_id,
            username=user_.username,
            password_hash=user_.password_hash,
            nickname=user_.nickname,
            email=user_.email,
            rejection_count=0))
        transaction.commit()
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

    username = All(
        validators.String(
            min=USERNAME_LENGTH_MINIMUM,
            max=USERNAME_LENGTH_MAXIMUM,
            strip=True),
        Unique('username', 'That username already exists'))
    password = All(
        validators.MinLength(
            PASSWORD_LENGTH_MINIMUM,
            not_empty=True),
        SecurePassword())
    nickname = All(
        validators.UnicodeString(
            min=NICKNAME_LENGTH_MINIMUM,
            max=NICKNAME_LENGTH_MAXIMUM,
            strip=True),
        Unique('nickname', 'That nickname already exists'))
    email = All(
        validators.Email(
            not_empty=True, 
            strip=True),
        Unique('email', 'That email is reserved for another account'))


def format_tokens(user):
    'Format unicode into token'
    return ['x' + base64.urlsafe_b64encode(user.nickname.encode('utf8')).replace('=', '+')] + user.get_groups()


def parse_tokens(tokens):
    'Parse unicode from token'
    nickname = base64.urlsafe_b64decode(tokens[0][1:].replace('+', '=')).decode('utf8')
    return nickname, tokens[1:]


def get_minutes_offset(request):
    try:
        return int(request.params.get('minutes_offset', request.session.get('person.minutes_offset', MINUTES_OFFSET_DEFAULT)))
    except ValueError:
        return MINUTES_OFFSET_DEFAULT



class AuthenticationPolicy(object):
    'A custom Pyramid authentication policy using Beaker'

    def authenticated_userid(self, request):
        'Return userID if authenticated'

    def effective_principals(self, request):
        'Return identifiers'

    def remember(self, request, userID, **kw):
        'Remember user'
        # Prepare shortcut
        session = request.session
        # Save userID
        session['user.id'] = userID
        # Save keywords as user attributes
        for key, value in kw.iteritems():
            session['user.' + key] = value
        # Save session
        session.save()

    def forget(self, request):
        'Forget user'
        # Prepare shortcut
        # If the user is authenticated,
        if 'user.id' in session:
            # Delete keys from session
