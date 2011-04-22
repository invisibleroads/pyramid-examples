'Data models'
import transaction
from sqlalchemy import func, Column, ForeignKey, Integer, String, LargeBinary, Unicode, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, column_property
from sqlalchemy.orm.properties import ColumnProperty
from zope.sqlalchemy import ZopeTransactionExtension

from auth.libraries.tools import hash_string, make_random_string
from auth.parameters import *


db = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class CaseInsensitiveComparator(ColumnProperty.Comparator):
    'A case-insensitive SQLAlchemy comparator for unicode or string columns'

    def __eq__(self, other):
        'Return True if the lowercase of both columns are equal'
        return func.lower(self.__clause_element__()) == func.lower(other)


class User(Base):
    'A user'
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = column_property(
        Column(String(USERNAME_LEN_MAX), unique=True), 
        comparator_factory=CaseInsensitiveComparator)
    password_hash = Column(LargeBinary(32))
    nickname = column_property(
        Column(Unicode(NICKNAME_LEN_MAX), unique=True),
        comparator_factory=CaseInsensitiveComparator)
    email = column_property(
        Column(String(EMAIL_LEN_MAX), unique=True), 
        comparator_factory=CaseInsensitiveComparator)
    is_super = Column(Boolean, default=False)
    rejection_count = Column(Integer, default=0)
    offset = Column(Integer, default=0)
    when_login = Column(DateTime)
    sms_addresses = relationship('SMSAddress')

    def __repr__(self):
        return "<User('%s')>" % self.email

    @property
    def groups(self):
        return ['x'] if self.is_super else []


class User_(Base):
    'An unconfirmed change to a user account'
    __tablename__ = 'users_'
    id = Column(Integer, primary_key=True)
    username = column_property(
        Column(String(USERNAME_LEN_MAX)), 
        comparator_factory=CaseInsensitiveComparator)
    password_hash = Column(LargeBinary(32))
    nickname = column_property(
        Column(Unicode(NICKNAME_LEN_MAX)), 
        comparator_factory=CaseInsensitiveComparator)
    email = column_property(
        Column(String(EMAIL_LEN_MAX)), 
        comparator_factory=CaseInsensitiveComparator)
    user_id = Column(ForeignKey('users.id'))
    ticket = Column(String(TICKET_LEN), unique=True)
    when_expired = Column(DateTime)

    def __repr__(self):
        return "<User_('%s')>" % self.email


class SMSAddress(Base):
    'An SMS address'
    __tablename__ = 'sms_addresses'
    id = Column(Integer, primary_key=True)
    email = column_property(
        Column(String(EMAIL_LEN_MAX)), 
        comparator_factory=CaseInsensitiveComparator)
    user_id = Column(ForeignKey('users.id'))
    code = Column(String(CODE_LEN))

    def __repr__(self):
        return "<SMSAddress('%s')>" % self.email


def initialize_sql(engine):
    'Create tables and insert data'
    # Create tables
    db.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # If the tables are empty,
    if not db.query(User).count():
        # Prepare data
        userPacks = [
            ('admin', make_random_string(PASSWORD_LEN), u'Admin', 'admin@example.com', True),
            ('user', make_random_string(PASSWORD_LEN), u'User', 'user@example.com', False), 
        ]
        # Insert data
        userTemplate = '\nUsername\t%s\nPassword\t%s\nNickname\t%s\nEmail\t\t%s'
        for username, password, nickname, email, is_super in userPacks:
            print userTemplate % (username, password, nickname, email)
            db.add(User(username=username, password_hash=hash_string(password), nickname=nickname, email=email, is_super=is_super))
        print
        transaction.commit()
