'Views'


def home(request):
    pass


def protected(request):
    return {'content': 'Protected'}


def privileged(request):
    return {'content': 'Privileged'}
