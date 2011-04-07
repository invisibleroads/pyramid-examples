'Database models'
from sqlalchemy import func, Column, ForeignKey, Integer, String, LargeBinary, Unicode, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, column_property
from sqlalchemy.orm.properties import ColumnProperty
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

from auth.libraries.tools import hash_string, make_random_string
from auth.parameters import USERNAME_LENGTH_MAXIMUM, PASSWORD_LENGTH, NICKNAME_LENGTH_MAXIMUM, EMAIL_LENGTH_MAXIMUM, TICKET_LENGTH


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
        Column(String(USERNAME_LENGTH_MAXIMUM), unique=True), 
        comparator_factory=CaseInsensitiveComparator)
    password_hash = Column(LargeBinary(32))
    nickname = column_property(
        Column(Unicode(NICKNAME_LENGTH_MAXIMUM), unique=True),
        comparator_factory=CaseInsensitiveComparator)
    email = column_property(
        Column(String(EMAIL_LENGTH_MAXIMUM), unique=True), 
        comparator_factory=CaseInsensitiveComparator)
    is_super = Column(Boolean, default=False)
    minutes_offset = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    when_login = Column(DateTime)
    sms_addresses = relationship('SMSAddress')

    def __repr__(self):
        return "<User('%s')>" % self.email

    def get_groups(self):
        return ['super'] if self.is_super else []


class UserCandidate(Base):
    'A user candidate'
    __tablename__ = 'user_candidates'
    id = Column(Integer, primary_key=True)
    username = column_property(
        Column(String(USERNAME_LENGTH_MAXIMUM)), 
        comparator_factory=CaseInsensitiveComparator)
    password_hash = Column(LargeBinary(32))
    nickname = column_property(
        Column(Unicode(NICKNAME_LENGTH_MAXIMUM)), 
        comparator_factory=CaseInsensitiveComparator)
    email = column_property(
        Column(String(EMAIL_LENGTH_MAXIMUM)), 
        comparator_factory=CaseInsensitiveComparator)
    user_id = Column(ForeignKey('users.id'))
    ticket = Column(String(TICKET_LENGTH), unique=True)
    when_expired = Column(DateTime)

    def __repr__(self):
        return "<UserCandidate('%s')>" % self.email


class SMSAddress(Base):
    'An SMS address'
    __tablename__ = 'sms_addresses'
    id = Column(Integer, primary_key=True)
    email = column_property(
        Column(String(EMAIL_LENGTH_MAXIMUM), unique=True), 
        comparator_factory=CaseInsensitiveComparator)
    owner_id = Column(ForeignKey('users.id'))
    is_active = Column(Boolean, default=False)

    def __repr__(self):
        return "<SMSAddress('%s')>" % self.email


def initialize_sql(engine):
    'Create tables and insert data'
    # Create tables
    db.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # If the tables are empty,
    if not db.query(User).first():
        # Prepare data
        userPacks = [
            (
                'user', 
                make_random_string(PASSWORD_LENGTH), 
                u'User', 
                'user@example.com', 
                False,
            ), (
                'administrator', 
                make_random_string(PASSWORD_LENGTH), 
                u'Administrator', 
                'administrator@example.com', 
                True,
            ),
        ]
        # Insert data
        userTemplate = '\nUsername\t{}\nPassword\t{}\nNickname\t{}\nEmail\t\t{}'
        for username, password, nickname, email, is_super in userPacks:
            print userTemplate.format(username, password, nickname, email)
            user = User(
                username=username, 
                password_hash=hash_string(password), 
                nickname=nickname,
                email=email,
                is_super=is_super)
            db.add(user)
        print
        transaction.commit()
