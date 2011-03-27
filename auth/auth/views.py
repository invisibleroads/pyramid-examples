"""Views"""
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

from auth.models import DBSession, User, hashString
from auth import format_tokens


# Core

def index(request):
    db = DBSession()
    return dict(users=db.query(User).all())

def login(request):
    if request.url == request.route_url('login'):
        targetURL = request.params.get('targetURL', request.route_url('index'))
        if 'submitted' in request.params:
            username = request.params.get('username', '')
            password_hash = hashString(request.params.get('password', ''))
            db = DBSession()
            user = db.query(User).filter(
                (User.username==username) & 
                (User.password_hash==password_hash)
            ).first()
            if user:
                headers = remember(request, user.id, tokens=format_tokens(user))
                return HTTPFound(location=targetURL, headers=headers)
    else:
        targetURL = request.url
    # Return
    return dict(targetURL=targetURL)

def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('index'), headers=headers)

def public(request):
    return dict(content='Public')

def protected(request):
    return dict(content='Protected')

def privileged(request):
    return dict(content='Privileged')
