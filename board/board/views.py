'Views'
import transaction
from beaker.cache import cache_region, region_invalidate

from board.models import db, Post


# Core

def index(request):
    return {'posts': get_posts()}

def add(request):
    text = request.params.get('text', '').strip()
    if text:
        db.add(Post(text))
        transaction.commit()
        region_invalidate(get_posts, None)
    return index(request)


# Side

@cache_region('minute')
def get_posts():
    return db.query(Post).order_by(Post.id.desc()).all()
