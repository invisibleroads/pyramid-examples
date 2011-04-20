from sqlalchemy.orm import joinedload


@view_config(route_name='user_update', renderer='users/change.mak', request_method='GET', permission='protected')
def update(request):
    'Show account update page'
    # Render
    user = db.query(User).options(joinedload(User.sms_addresses)).get(h.getUserID())
    c.isNew = False
    c.smsAddresses = user.sms_addresses
    # Return
    return htmlfill.render(render('/people/change.mak'), {
        'username': user.username,
        'nickname': user.nickname,
        'email': user.email,
    })


@view_config(route_name='user_update', renderer='json', request_method='POST', permission='protected')
def update_(request):
    'Update account'
    # Initialize
    userID = h.getUserID()
    # If the user is trying to update SMS information,
    if 'smsAddressID' in request.params:
        # Load
        action = request.params.get('action')
        smsAddressID = request.params['smsAddressID']
        smsAddress = db.query(SMSAddress).filter((SMSAddress.id==smsAddressID) & (SMSAddress.owner_id==userID)).first()
        if not smsAddress:
            return dict(isOk=0, message='Could not find smsAddressID=%s corresponding to userID=%s' % (smsAddressID, userID))
        # If the user is trying to activate an SMS address,
        elif action == 'activate':
            smsAddress.is_active = True
        # If the user is trying to deactivate an SMS address,
        elif action == 'deactivate':
            smsAddress.is_active = False
        # If the user is trying to remove an SMS address,
        elif action == 'remove':
            db.delete(smsAddress)
        # Otherwise,
        else:
            return dict(isOk=0, message='Command not recognized')
        # Commit and return
        db.commit()
        return dict(isOk=1)
    # If the user is trying to update account information,
    else:
        # Send update confirmation email
        return save_user_(request, dict(request.params), 'update', db.query(User).get(userID))


@view_config(route_name='user_reset', renderer='json', request_method='POST', permission='__no_permission_required__')
def reset(request):
    'Reset password'
    # Get email
    email = request.params.get('email')
    # Try to load the user
    user = db.query(User).filter(User.email==email).first()
    # If the email is not in our database,
    if not user: 
        return dict(isOk=0)
    # Reset account
    return save_user_(request, dict(
        username=user.username, 
        password=make_random_string(PASSWORD_LENGTH), 
        nickname=user.nickname, 
        email=user.email
    ), 'reset', user)
