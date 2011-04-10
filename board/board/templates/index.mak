<!doctype html>
<html>
<head>
	<meta http-equiv='Content-Type' content='text/html;charset=UTF-8'/>
	<title>Pyramid example: ${SITE_NAME}</title>
</head>
<body>
	<input id=text>
	<input id=add type=button value=Add>
	<div id=posts>
		<%include file='index_.mak'/>
	</div>
	<script src="${request.static_url('board:static/jquery-1.5.2.min.js')}"></script>
	<script>
		function add() {
			// Get text
			var text = $.trim($('#text').val());
			// Exit if the text is empty
			if (text.length == 0) {
				$('#text').focus();
				return;
			}
			// Add post
			$.post("${request.route_url('add')}", {
				token: '${token}',
				text: text
			}, function(data) {
				$('#posts').html(data);
				$('#text').val('');
			});
		}
		$('#add').click(add);
		$('#text').keydown(function(e) {
			if (e.keyCode == 13) add();
		}).focus();
	</script>
</body>
</html>
