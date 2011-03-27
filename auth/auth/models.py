"""Database models"""
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, LargeBinary, Unicode, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
import hashlib


USERNAME_LEN_MAX = 32
NICKNAME_LEN_MAX = 32


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    """A user"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(USERNAME_LEN_MAX), unique=True)
    password_hash = Column(LargeBinary(32))
    nickname = Column(Unicode(NICKNAME_LEN_MAX), unique=True)
    is_super = Column(Boolean, default=False)

    def __init__(self, username, password_hash, nickname, is_super=False):
        self.username = username
        self.password_hash = password_hash
        self.nickname = nickname
        self.is_super = 1 if is_super else 0

    def get_groups(self):
        return ['super'] if self.is_super else []


def initialize_sql(engine):
    """Create tables and insert data"""
    # Create tables
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # Insert data
    db = DBSession()
    try:
        userPacks = [
            ('basic', 'basic', u'привет', False),
            ('super', 'super', u'спасибо', True),
        ]
        for username, password, nickname, is_super in userPacks:
            user = User(username, hashString(password), nickname, is_super)
            db.add(user)
        transaction.commit()
    except IntegrityError:
        db.rollback()
    # Return
    return db


def hashString(string): 
    'Compute the hash of the string'
    return hashlib.sha256(string).digest()
