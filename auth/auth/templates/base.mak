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
	path = request.path
	linkPacks = [
		('Home', '/'),
		('Users', request.route_path('user_index')),
	]
	if USER_ID:
		linkPacks.append((USER_NICKNAME, request.route_path('user_update')))
	%>
% for linkName, linkPath in linkPacks:
	&nbsp;
	% if linkPath != path:
		<a href='${linkPath}' class='hover link off'>${linkName}</a>
	% else:
		<b>${linkName}</b>
	% endif
% endfor
	&nbsp;
	% if USER_ID:
		<a href="${request.route_path('user_logout', _query=dict(url=request.path))}" class='hover link off'>Logout</a>
	% elif path != request.route_path('user_login') and request.exception.__class__.__name__ != 'Forbidden':
		<a href="${request.route_path('user_login', _query=dict(url=request.path))}" class='hover link off'>Login</a>
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
    $('.hover').live({
        mouseenter: function() {$(this).removeClass('off').addClass('on')},
        mouseleave: function() {$(this).removeClass('on').addClass('off')}
    });
	function getNumber(x) {return /\d+/.exec(x)[0]}
	function getID(obj) {return getNumber(obj.id)}
    function ajax(type, url, data, callback) {
        $.ajax({
            type: type,
            url: url,
            data: data,
            dataType: 'json',
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == 'parsererror') {
                    window.location = "${request.route_path('user_login')}?url=" + window.location.pathname;
                }
            }
        });
    }
    function get(url, data, callback) {return ajax('GET', url, data, callback)}
    function post(url, data, callback) {return ajax('POST', url, data, callback)}
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
