<%inherit file='/base.mak'/>

<%def name='title()'>Users</%def>

<%def name='css()'>
	.nickname {text-align: center}
	.when_login {text-align: center}
</%def>

<%def name='toolbar()'>
	${len(users)} users
</%def>

<%def name='root()'>
	<link rel=stylesheet href="${request.static_url('auth:static/dataTables/style.css')}">
	<script src="${request.static_url('auth:static/dataTables/jquery.dataTables.min.js')}"></script>
</%def>

<%def name='js()'>
	function computeTableHeight() {
		return $(window).height() - 100;
	}
	$('#users').dataTable({
		'bInfo': false,
		'bPaginate': false,
		'sScrollY': computeTableHeight(),
		'oLanguage': {'sSearch': 'Filter'}
	});
	$(window).bind('resize', function() {
		$('.dataTables_scrollBody').height(computeTableHeight());
	});
	$('.dataTables_filter input').focus();
</%def>

<table id=users>
	<thead>
		<tr>
			<th class=nickname>Nickname</th>
			<th class=when_login>Last Login</th>
		</tr>
	</thead>
	<tbody>
	% for user in users:
		<tr>
			<td class=nickname>${user.nickname}</td>
			<td class=when_login>
			% if user.when_login:
				${user.when_login}
			% endif
			</td>
		</tr>
	% endfor
	</tbody>
</table>
