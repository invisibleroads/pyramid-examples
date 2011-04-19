'Pages demonstrating access control'
from pyramid.view import view_config


def includeme(config):
    config.add_route('page_public', '')
    config.add_route('page_protected', '/protected')
    config.add_route('page_privileged', '/privileged')


@view_config(route_name='page_public', renderer='page.mak', permission='__no_permission_required__')
def public(request):
    return dict()


@view_config(route_name='page_protected', renderer='page.mak', permission='protected')
def protected(request):
    return dict()


@view_config(route_name='page_privileged', renderer='page.mak', permission='privileged')
def privileged(request):
    return dict()
