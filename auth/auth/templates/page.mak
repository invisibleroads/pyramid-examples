<%inherit file='/base.mak'/>

<div id=pages>
% for routeName in 'page_public', 'page_protected', 'page_privileged':
	<%
	path = request.route_path(routeName)
	name = routeName[5:].capitalize()
	%>
	% if request.path == path:
		<b>${name}</b>
	% else:
		<a href="${path}" class='hover link off'>${name}</a>
	% endif
	<br>
% endfor
</div>
