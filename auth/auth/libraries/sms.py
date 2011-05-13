'Application-specific functions for processing SMS messages'
import re
import imapIO
import collections
import transaction
import ConfigParser
from email.utils import parseaddr
from sqlalchemy.orm import joinedload
from formencode import validators, Invalid

from auth.models import db, User, SMSAddress


pattern_registration = re.compile(r'(\d+)\W+(.*)')


def process(settings):
    'Process messages on IMAP server'
    imapServer = connect(settings)
    countByKey = collections.defaultdict(int)
    # Walk messages in inbox sorted by arrival time,
    for email in imapServer.walk('inbox', sortCriterion='ARRIVAL'):
        # If the user is trying to register an SMS address,
        if processRegistration(email):
            countByKey['registrations'] += 1
        # Mark email as deleted
        email.deleted = True
        countByKey['messages'] += 1
    # Finalize
    transaction.commit()
    imapServer.expunge()
    # Return
    return countByKey


def connect(settings):
    'Connect to IMAP server'
    try:
        imapParams = [settings[x] for x in
            'sms.imap.host', 
            'sms.imap.port', 
            'sms.imap.username', 
            'sms.imap.password']
    except KeyError, error:
        raise KeyError('Missing %s in configuration file' % error)
    try:
        imapServer = imapIO.connect(*imapParams)
    except imapIO.IMAPError, error:
        return error
    return imapServer


def processRegistration(email):
    'Process an SMS address registration'
    # Get userID and code
    match = pattern_registration.match(email.subject)
    if not match:
        return False
    userID, userCode = match.groups()
    userID = int(userID)
    fromWhom = parseaddr(email.fromWhom)[1]
    # Make sure we have a proper email address
    try:
        fromWhom = validators.Email(not_empty=True).to_python(fromWhom)
    except Invalid:
        return False
    # If userID is zero, then the sender wants to unregister his or her address
    if userID == 0:
        db.query(SMSAddress).filter_by(email=fromWhom).delete()
        return True
    # Load
    user = db.query(User).filter_by(id=userID, code=userCode).options(joinedload(User.sms_addresses)).first()
    # If the user doesn't exist,
    if not user:
        return False
    # If we have registered the address already,
    if fromWhom in (x.email for x in user.sms_addresses):
        return True
    # Add
    db.add(SMSAddress(email=fromWhom, user_id=userID))
    return True
