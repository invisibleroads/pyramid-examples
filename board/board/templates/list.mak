<!doctype html>
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
</head>
<body>
% for post in posts:
	<p id=${post.id}>
		${post.text}
	</p>
% endfor
</body>
</html>
