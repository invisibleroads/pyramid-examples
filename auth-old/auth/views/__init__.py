'Views'


def public(request):
    return dict()


def protected(request):
    return dict(content='Protected')


def privileged(request):
    return dict(content='Privileged')
