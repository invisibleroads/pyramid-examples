"""Views"""
from board.models import DBSession
from board.models import Post
 

def list(request):
    db = DBSession()
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return {'posts': posts}
