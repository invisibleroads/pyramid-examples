<% 
	import datetime
	now = datetime.datetime.utcnow()
%>
% for offset in xrange(1410, -1, -30):
<option value=${offset}>${(now - datetime.timedelta(minutes=offset)).strftime('%I:%M %p')}</option>
% endfor
