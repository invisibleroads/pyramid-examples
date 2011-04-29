<%inherit file='/base.mak'/>

<%def name='title()'>Account ${'Update' if user else 'Registration'}</%def>

<%def name='css()'>
td {padding-right: 1em}
.smsAddressCode {display: none}
.smsAddressInactive {color: gray}
.flag {font-size: xx-small; vertical-align: middle}
</%def>

<%def name='js()'>
% if user:
var token = '${request.session.get_csrf_token()}';
% endif
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
	post("${request.route_path('user_update' if user else 'user_register')}", {
	% if user:
		token: token,
	% endif
        username: username,
        password: password,
        nickname: nickname,
        email: email
    }, function(data) {
        var messageByID = {};
        if (data.isOk) {
			messageByID['status'] = "Please check your email to ${'finalize changes to' if user else 'create'} your account.";
        } else {
            $('.lockOnSave').removeAttr('disabled');
            messageByID = data.errorByID;
        }
        showMessageByID(messageByID);
    });
}
$('#save').click(save);
% if user:
// Add SMS address after user presses ENTER key in input box
$('#smsAddressEmail').live('keydown', function(e) {
	if (e.keyCode == 13) {
		var smsAddressEmail = $.trim(this.value);
		if (!smsAddressEmail.length) {
			return showMessageByID({smsAddressEmail: 'Please enter a value'});
		}
		post("${request.route_path('user_update')}", {
			token: token,
			smsAddressAction: 'add',
			smsAddressEmail: smsAddressEmail
		}, function(data) {
			if (data.isOk) {
				$('#smsAddresses').html(data.content);
			} else {
				showMessageByID({smsAddressEmail: data.message});
			}
		});
	}
});
// Activate SMS address after user enters correct code
$('.smsAddressCode').live('keydown', function() {
	if (e.keyCode == 13) {
		var smsAddressID = getID(this), smsAddressCode = $(this), smsAddressEmail = $('#smsAddressEmail' + smsAddressID);
		smsAddressCode.attr('disabled', 'disabled');
		post("${request.route_path('user_update')}", {
			token: token,
			smsAddressAction: 'activate',
			smsAddressID: smsAddressID,
			smsAddressCode: smsAddressCode
		}, function(data) {
			if (data.isOk) {
				smsAddressCode.hide();
				smsAddressEmail.removeClass('smsAddressInactive').show();
			} else {
				alert(data.message);
				smsAddressCode.removeAttr('disabled').val('').focus();
			}
		});
	}
});
// Remove SMS address after user clicks on the button
$('.smsAddressRemove').live('click', function() {
	var smsAddressID = getID(this), smsAddress = $('#smsAddress' + smsAddressID);
	smsAddress.hide();
	post("${request.route_path('user_update')}", {
		token: token,
		smsAddressAction: 'remove',
		smsAddressID: smsAddressID
	}, function(data) {
		if (!data.isOk) {
			alert(data.message);
			smsAddress.show();
		}
	});
});
// Show SMS address code input box after user clicks on text
$('.smsAddressInactive').live({
	mouseenter: function() {
		$(this).append('<span class=flag>&nbsp; activate</span>');
	},
	mouseleave: function() {
		$(this).find('.flag').remove();
	},
	click: function() {
		$(this).hide();
		$('#smsAddressCode' + getID(this)).show().focus();
	}
});
% endif
// Let ENTER key traverse and submit form
$('#username').keydown(function(e) {if (e.keyCode == 13) $('#password').focus()});
$('#password').keydown(function(e) {if (e.keyCode == 13) $('#nickname').focus()});
$('#nickname').keydown(function(e) {if (e.keyCode == 13) $('#email').focus()});
$('#email').keydown(function(e) {if (e.keyCode == 13) save()});
// Focus
$('#username').focus();
</%def>

<%def name='toolbar()'>
${'Update your account' if user else 'Register for an account'}
</%def>

<table>
    <tr>
        <td><label for=username>Username</label></td>
        <td><input id=username class=lockOnSave autocomplete=off\
		% if user:
			value='${user.username}'
		% endif
		></td>
        <td id=m_username class=message>What you use to login</td>
    </tr>
    <tr>
        <td><label for=password>Password</label></td>
        <td><input id=password class=lockOnSave type=password autocomplete=off></td>
        <td id=m_password class=message>So you have some privacy</td>
    </tr>
    <tr>
        <td><label for=nickname>Nickname</label></td>
        <td><input id=nickname class=lockOnSave autocomplete=off\
		% if user:
			value='${user.nickname}'
		% endif
		></td>
        <td id=m_nickname class=message>How others see you</td>
    </tr>
    <tr>
        <td><label for=email>Email</label></td>
        <td><input id=email class=lockOnSave autocomplete=off\
		% if user:
			value='${user.email}'
		% endif
		></td>
        <td id=m_email class=message>To confirm changes to your account</td>
    </tr>
    <tr>
        <td></td>
		<td><input id=save class=lockOnSave type=button value="${'Update' if user else 'Register'}"></td>
        <td id=m_status class=message></td>
    </tr>
% if user:
    <tr>
        <td>&nbsp;</td>
    </tr>
    <tr>
		<td><label for=smsAddressEmail>SMS address</label></td>
		<td><input id=smsAddressEmail></td>
		<td id=m_smsAddressEmail class=message>For text message alerts</td>
    </tr>
	<tbody id=smsAddresses>
		<%include file='smsAddresses.mak'/>
	</tbody>
% endif
</table>
