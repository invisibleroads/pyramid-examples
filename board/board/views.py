'Views'
from pyramid.view import view_config
from beaker.cache import cache_region, region_invalidate
import transaction

from board.models import db, Post


def add_routes(config):
    'Add routes'
    config.add_route('index', '')
    config.add_route('debug', 'debug')


@view_config(route_name='index', renderer='index.mak', request_method='GET') 
def index(request):
    'List posts'
    return {'posts': get_posts()}


@view_config(route_name='index', renderer='index_.mak', request_method='POST') 
def index_(request):
    'Add a post'
    # Load
    text = request.params.get('text', '').strip()
    if text:
        # Add
        db.add(Post(text))
        transaction.commit()
        region_invalidate(get_posts, None)
    # Return
    return index(request)


@view_config(route_name='debug') 
def debug(request):
    'Enter debugger'
    raise Exception


@cache_region('minute')
def get_posts():
    return db.query(Post).order_by(Post.id.desc()).all()
