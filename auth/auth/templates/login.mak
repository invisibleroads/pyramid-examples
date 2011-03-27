<%inherit file='base.mak'/>

<form action="${request.route_url('login')}" method=POST>
<input type=hidden name=targetURL value='${targetURL}'>
<table>
	<tr>
		<td>Username</td>
		<td><input name=username></td>
	</tr>
	<tr>
		<td>Password</td>
		<td><input type=password name=password></td>
	</tr>
	<tr>
		<td></td>
		<td><input type=submit name=submitted value=Login></td>
	</tr>
</table>
</form>
