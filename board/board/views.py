'Views'
import transaction
from beaker.cache import cache_region, region_invalidate

from board.models import db, Post


# Core

def index(request):
    'List posts'
    return {'posts': get_posts()}

def add(request):
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


# Side

@cache_region('minute')
def get_posts():
    return db.query(Post).order_by(Post.id.desc()).all()
