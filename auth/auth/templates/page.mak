<%inherit file='/base.mak'/>

<div id=pages>
% for routeName in 'public', 'protected', 'privileged':
	<%
	url = request.route_url(routeName)
	%>
	% if request.url == url:
		<b>${routeName}</b>
	% else:
		<a href="${url}" class='hover link off'>${routeName}</a>
	% endif
	<br>
% endfor
</div>
