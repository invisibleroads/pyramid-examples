% for smsAddress in sorted(user.sms_addresses, key=lambda x: [x.is_active, x.email]):
	<%
	smsAddressID = smsAddress.id
	%>
	<div id=smsAddress${smsAddressID}
	% if not smsAddress.is_active:
		class=smsAddressInactive
	% endif
	>
		<input type=button id=smsAddressRemove${smsAddressID} class=smsAddressRemove title='Remove'>
		<span id=smsAddressEmail${smsAddressID} class=smsAddressEmail>
			<span class=text>${smsAddress.email}</span>
		</span>
    </div>
% endfor
