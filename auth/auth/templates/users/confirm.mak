We received your ${action} request for the following credentials.

Username: ${form['username']}
% if action == 'reset':
Password: ${form['password']}
% endif

Please click on the link below to complete your ${action}.
## ${request.relative_url(h.url('person_confirm', ticket=c.ghost.ticket), to_application=True)}

This ticket expires in ${TICKET_LIFESPAN_IN_HOURS} hours.
