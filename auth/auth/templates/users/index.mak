<%inherit file='/base.mak'/>

<%def name='title()'>Users</%def>

<%def name='css()'>
td {text-align: center}
</%def>

<%def name='toolbar()'>
${len(users)} users
</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('auth:static/dataTables/style.css')}">
<script src="${request.static_url('auth:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('auth:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
function computeTableHeight() {
	return $(window).height() - 100;
}
var usersTable = $('#users').dataTable({
	'aaSorting': [[1, 'desc']],
	'aoColumns': [
		{'sType': 'string'},
		{'sType': 'title-string'}
	],
	'bInfo': false,
	'bPaginate': false,
	'oLanguage': {'sSearch': 'Filter'},
	'sScrollY': computeTableHeight()
});
$(window).bind('resize', function() {
	$('.dataTables_scrollBody').height(computeTableHeight());
	usersTable.fnAdjustColumnSizing();
});
$('.dataTables_filter input').focus();
</%def>

<%!
import whenIO
%>

<table id=users>
	<thead>
		<tr>
			<th>Nickname</th>
			<th>Last Login</th>
		</tr>
	</thead>
	<tbody>
	% for user in users:
		<tr>
			<td>${user.nickname}</td>
			<td>
			% if user.when_login:
				<%
				when_login = user.when_login
				localWhenIO = whenIO.WhenIO(user.offset)
				%>
				<span title="${when_login.strftime('%Y%m%d%H%M%S')}"></span>
				${localWhenIO.format(when_login)} ${whenIO.format_offset(user.offset)}
			% else:
				<span title=''></span>
			% endif
			</td>
		</tr>
	% endfor
	</tbody>
</table>
