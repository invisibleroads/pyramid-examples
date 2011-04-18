<%inherit file='/base.mak'/>

<div id=pages>
% for routeName in 'page_public', 'page_protected', 'page_privileged':
	<%
	url = request.route_url(routeName)
	name = routeName[5:].capitalize()
	%>
	% if request.url == url:
		<b>${name}</b>
	% else:
		<a href="${url}" class='hover link off'>${name}</a>
	% endif
	<br>
% endfor
</div>
