"""Database models"""
import transaction
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


TEXT_LEN_MAX = 256


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Post(Base):
    """A board post"""
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    text = Column(Unicode(TEXT_LEN_MAX))

    def __init__(self, text):
        self.text = text


def initialize_sql(engine):
    """Create tables and insert data"""
    # Create tables
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # Insert data
    db = DBSession()
    if not db.query(Post).count():
        for text in u'one', u'two', u'three':
            db.add(Post(text))
        transaction.commit()
    # Return
    return db
