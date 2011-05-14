'Views'
from pyramid.view import view_config
from beaker.cache import cache_region, region_invalidate
import transaction

from board.models import db, Post


def includeme(config):
    'Add routes'
    config.scan(__name__)
    config.add_route('index', '')
    config.add_route('debug', 'debug')
    config.add_route('pdb', 'pdb')


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


@view_config(route_name='pdb') 
def debug(request):
    'Enter debugger'
    import pdb; pdb.set_trace()
    return {}


@cache_region('minute')
def get_posts():
    return db.query(Post).order_by(Post.id.desc()).all()
