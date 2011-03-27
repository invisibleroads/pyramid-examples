<%inherit file='base.mak'/>

<h1>Users</h1>
<table id=users>
	<tr>
		<th>Username</th>
		<th>Password</th>
		<th>Nickname</th>
		<th>Groups</th>
	</tr>
% for user in users:
	<tr>
		<td>${user.username}</td>
		<td>${user.username}</td>
		<td>${user.nickname}</td>
		<td>${', '.join(user.get_groups())}</td>
	</tr>
% endfor
</table>

<h1>Pages</h1>
<div id=pages>
	<a href="${request.route_url('public')}">Public</a><br>
	<a href="${request.route_url('protected')}">Protected</a><br>
	<a href="${request.route_url('privileged')}">Privileged</a><br>
</div>
