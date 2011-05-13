<%inherit file='/base.mak'/>

<div id=pages>
<%
routeNames = [
	'page_everyone',
	'page_authenticated',
	'page_active',
	'page_super',
]
%>
% for routeName in routeNames:
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
