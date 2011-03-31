## add datatables
<%inherit file='base.mako'/>

<%def name='title()'>Users</%def>

<%def name='toolbar()'>${len(users)} users</%def>

<table>
	<tr>
		<th>Nickname</th>
		<th>Last Login</th>
	</tr>
% for user in users:
	<tr>
		<td>${user.nickname}</td>
		<td>${user.when_login}</td>
	</tr>
% endfor
</table>
