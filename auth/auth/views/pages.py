'Pages demonstrating access control'
from pyramid.view import view_config


def includeme(config):
    config.scan(__name__)
    config.add_route('page_everyone', '')
    config.add_route('page_authenticated', '/authenticated')
    config.add_route('page_active', '/active')
    config.add_route('page_super', '/super')


@view_config(route_name='page_everyone', renderer='page.mak', permission='__no_permission_required__')
def everyone(request):
    return dict()


@view_config(route_name='page_authenticated', renderer='page.mak', permission='authenticated')
def authenticated(request):
    return dict()


@view_config(route_name='page_active', renderer='page.mak', permission='active')
def active(request):
    return dict()


@view_config(route_name='page_super', renderer='page.mak', permission='super')
def super(request):
    return dict()
