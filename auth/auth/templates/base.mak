<!doctype html>
<html>
<head>
	<meta http-equiv='Content-Type' content='text/html;charset=UTF-8'/>
	<meta name='author' content='Roy Hyunjin Han'/>
	<title>${SITE_NAME} ${self.title()}</title>
	<link rel='shortcut icon' href='${request.static_url('auth:static/favicon.ico')}'/>
	<link rel=stylesheet href='${request.static_url('auth:static/style.css')}'>
	<style>${self.css()}</style>
</head>
<body>
<div id=header>
	<div id=toolbar>${self.toolbar()}</div>
	<div id=navigation>${self.navigation()}
	<%
		linkPacks = [
			('Users', request.route_url('user_index')),
		]
		if USER_ID:
			linkPacks.append((USER_NICKNAME, request.route_url('user_update')))
	%>
% for linkName, linkURL in linkPacks:
	&nbsp;
	% if request.url != linkURL:
		<a href='${linkURL}' class='hover link off'>${linkName}</a>
	% else:
		<b>${linkName}</b>
	% endif
% endfor
	% if USER_ID:
		&nbsp;
		<a href="${request.route_url('user_logout', url=request.path)}" class='hover link off'>Logout</a>
	% elif request.url != request.route_url('user_login'):
		&nbsp;
		<a href="${request.route_url('user_login', url=request.path)}" class='hover link off'>Login</a>
	% else:
		<b>Login</b>
	% endif
	</div>
</div>
<div id=main>
	${next.body()}
</div>
<script src="${request.static_url('auth:static/jquery-1.5.2.min.js')}"></script>
${self.root()}
<script>
	$('.hover').live('hover', function(e) {
		$(this).toggleClass('off on');
	});
	function getNumber(x) {return /\d+/.exec(x)[0]}
	function getID(obj) {return getNumber(obj.id)}
	${self.js()}
</script>
</body>
</html>\

<%def name='title()'></%def>\
<%def name='css()'></%def>\
<%def name='toolbar()'></%def>\
<%def name='navigation()'></%def>\
<%def name='root()'></%def>\
<%def name='js()'></%def>\