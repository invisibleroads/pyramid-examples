"""Views"""
import transaction

from board.models import DBSession, Post
 

def index(request):
    db = DBSession()
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return {'posts': posts}


def add(request):
    db = DBSession()
    text = request.params.get('text', '').strip()
    if text:
        db.add(Post(text))
        transaction.commit()
    return index(request)
