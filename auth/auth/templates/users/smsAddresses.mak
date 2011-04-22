% for smsAddress in sorted(user.sms_addresses, key=lambda x: [-len(x.code), x.email]):
	<%
	smsAddressID = smsAddress.id
	%>
    <tr id=smsAddress${smsAddressID}>
        <td>
            <input type=button id=smsAddressRemove${smsAddressID} class=smsAddressRemove value=- title='Remove'>
		</td>
		<td colspan=2>
			<span id=smsAddressEmail${smsAddressID} class="${'smsAddressInactive' if smsAddress.code else ''}">${smsAddress.email}</span>
		% if smsAddress.code:
			<input id=smsAddressCode${smsAddressID} class=smsAddressCode>
		% endif
		</td>
    </tr>
% endfor
