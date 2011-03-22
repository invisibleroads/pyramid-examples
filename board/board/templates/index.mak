<!doctype html>
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
</head>
<body>
	<input id=text>
	<input id=add type=button value=Add>
	<div id=posts>
		<%include file="index_.mak"/>
	</div>
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
	<script src="${request.static_url('board:static/index.js')}"></script>
</body>
</html>
