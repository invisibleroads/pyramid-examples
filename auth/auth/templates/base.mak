<!doctype html>
<head>
	<meta http-equiv='Content-Type' content='text/html;charset=UTF-8'/>
	<title>Pyramid example: ${SITE_NAME} ${self.title()}</title>
</head>
<html>
	<body>
		% if not USER_ID:
			<a href="${request.route_url('login')}">Login</a>
			<br>
		% else:
			${USER_NICKNAME}
			<a href="${request.route_url('logout')}">Logout</a>
			<br>
		% endif
		${next.body()}
	</body>
</html>

<%def name='title()'></%def>
