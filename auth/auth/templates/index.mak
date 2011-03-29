<%inherit file='base.mak'/>

<div id=pages>
	<a href="${request.route_url('public')}">Public</a><br>
	<a href="${request.route_url('protected')}">Protected</a><br>
	<a href="${request.route_url('privileged')}">Privileged</a><br>
</div>
