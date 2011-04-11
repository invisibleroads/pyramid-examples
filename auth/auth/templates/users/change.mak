## add CSRF
<%inherit file='/base.mak'/>

<%def name='title()'>Account ${'Registration' if isNew else 'Update'}</%def>

<%def name='css()'>
label {padding-right: 1em}
.message {padding-left: 1em}
.inactive {color: gray}
</%def>

<%def name='js()'>
// Save default descriptions
function getFieldID(x) {return x.id.match(/m_(.*)/)[1]}
function showMessageByID(messageByID) {
	var focused = false;
	$('.message').each(function() {
		var id = getFieldID(this);
        var message = messageByID[id];
        if (message) {
            $(this).html('<b>' + message + '</b>');
            if (!focused) {
                $('#' + id).focus().select();
                focused = true;
            }
        } else {
            $(this).html(defaultByID[id]);
        }
	});
}
var defaultByID = {};
$('.message').each(function() {
	var id = getFieldID(this);
    defaultByID[id] = $(this).html();
});
// Define button behavior
function save() {
    var username = $('#username').val(),
        password = $('#password').val(), 
        nickname = $('#nickname').val(), 
        email = $('#email').val();
    $('.lockOnSave').attr('disabled', 'disabled');
    $.post("${request.route_url('user_register' if isNew else 'user_update')}", {
        username: username,
        password: password,
        nickname: nickname,
        email: email
    }, function(data) {
        var messageByID = {};
        if (data.isOk) {
            messageByID['status'] = "Please check your email to ${'create' if isNew else 'finalize changes to'} your account.";
        } else {
            $('.lockOnSave').removeAttr('disabled');
            messageByID = data.errorByID;
        }
        showMessageByID(messageByID);
    });
}
$('#save').click(save);
$('.updateSMSAddress').click(function() {
    var button = $(this), action = button.val().toLowerCase(), smsAddressID = getID(this), smsAddressRow = $('#smsAddress' + smsAddressID), smsAddressEmail = $('#smsAddressEmail' + smsAddressID);
    switch (action) {
        case 'activate':
            smsAddressEmail.removeClass('inactive');
            button.val('Deactivate');
            break;
        case 'deactivate':
            smsAddressEmail.addClass('inactive');
            button.val('Activate');
            break;
        case 'remove':
            smsAddressRow.hide();
            break;
    }
    $.post("${request.route_url('user_update')}", {
		smsAddressID: smsAddressID, 
		action: action
	}, function(data) {
        if (!data.isOk) {
            switch (action) {
                case 'activate':
                    smsAddressEmail.addClass('inactive');
                    button.val('Activate');
                    break;
                case 'deactivate':
                    smsAddressEmail.removeClass('inactive');
                    button.val('Deactivate');
                    break;
                case 'remove':
                    smsAddressRow.show();
                    break;
            }
            alert(data.message);
        }
    });
});
// Let ENTER key traverse and submit form
$('#username').keydown(function(e) {if (e.keyCode == 13) $('#password').focus()});
$('#password').keydown(function(e) {if (e.keyCode == 13) $('#nickname').focus()});
$('#nickname').keydown(function(e) {if (e.keyCode == 13) $('#email').focus()});
$('#email').keydown(function(e) {if (e.keyCode == 13) save()});
// Focus
$('#username').focus();
</%def>

<%def name='toolbar()'>
${'Register for an account' if isNew else 'Update your account'}
</%def>

<table>
    <tr>
        <td><label for=username>Username</label></td>
        <td><input id=username class=lockOnSave autocomplete=off value='${username | h}'></td>
        <td id=m_username class=message>What you use to login</td>
    </tr>
    <tr>
        <td><label for=password>Password</label></td>
        <td><input id=password class=lockOnSave type=password autocomplete=off></td>
        <td id=m_password class=message>So you have some privacy</td>
    </tr>
    <tr>
        <td><label for=nickname>Nickname</label></td>
        <td><input id=nickname class=lockOnSave autocomplete=off value='${nickname | h}'></td>
        <td id=m_nickname class=message>How others see you</td>
    </tr>
    <tr>
        <td><label for=email>Email</label></td>
        <td><input id=email class=lockOnSave autocomplete=off value='${email | h}'></td>
        <td id=m_email class=message>To confirm changes to your account</td>
    </tr>
    <tr>
        <td></td>
        <td><input id=save class=lockOnSave type=button value="${'Register' if isNew else 'Update'}"></td>
        <td id=m_status class=message></td>
    </tr>
% if not isNew:
    <tr>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td colspan=3>Send ${h.getPersonID()} as a text message to ${config['sms.email']} for SMS alerts</td>
    </tr>
% for smsAddress in sorted(smsAddresses, key=lambda x: -x.is_active):
    <tr id=smsAddress${smsAddress.id}>
        <td></td>
        <td id=smsAddressEmail${smsAddress.id}\
        % if not smsAddress.is_active:
            class=inactive\
        % endif
        >${smsAddress.email}</td>
        <td>
            <input type=button id=removeSMSAddress${smsAddress.id} class=updateSMSAddress value=Remove>
		% if not smsAddress.is_active:
            <input type=button id=activateSMSAddress${smsAddress.id} class=updateSMSAddress value=Activate>
		% endif
        </td>
    </tr>
% endfor
% endif
</table>
