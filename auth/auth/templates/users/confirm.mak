We received your ${action} request for the following credentials.

Username: ${form['username']}
% if action == 'reset':
Password: ${form['password']}
% endif

Please open the link below to complete your ${action}.
${request.route_url('user_confirm', ticket=ticket)}

This ticket expires in ${TICKET_HOURS} hours.
