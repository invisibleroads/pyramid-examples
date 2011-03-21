"""Views"""
import transaction

from board.models import DBSession
from board.models import Post
 

def list(request):
    db = DBSession()
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return {'posts': posts}


def add(request):
    db = DBSession()
    text = request.POST.get('text', '').strip()
    if text:
        db.add(Post(text))
        transaction.commit()
    return list(request)
