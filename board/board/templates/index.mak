<!doctype html>
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
	<script src="${request.static_url('board:static/jquery-1.5.1.min.js')}"></script>
	<script>
		$(document).ready(function() {
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
		});
	</script>
</head>
<body>
	<input id=text>
	<input id=add type=button value=Add>
	<div id=posts>
		<%include file="index_.mak"/>
	</div>
</body>
</html>
