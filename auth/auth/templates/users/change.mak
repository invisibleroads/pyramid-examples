<%inherit file='/base.mak'/>

<%def name='title()'>Account ${'Update' if user else 'Registration'}</%def>

<%def name='css()'>
td {padding-right: 1em}
.smsAddressInactive .text {color: gray}
.flag {color: darkblue}
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
// Mutate token
$('#mutate').click(function() {
	$.post("${request.route_path('user_mutate')}", {
		token: token
	}, function(data) {
		if (data.isOk) {
			$('#m_status').html('Token mutated successfully');
			$('#userCode').html(data.code);
		} else {
			$('#m_status').html(data.message);
		}
	});
});
// Remove SMS address after user clicks on the button
$('.smsAddressRemove').live('click', function() {
	var smsAddressID = getID(this), smsAddress = $('#smsAddress' + smsAddressID);
	smsAddress.hide();
	post("${request.route_path('user_update')}", {
		token: token,
		smsAddressID: smsAddressID,
		smsAddressAction: 'remove'
	}, function(data) {
		if (!data.isOk) {
			alert(data.message);
			smsAddress.show();
		}
	});
});
// Activate SMS address after user clicks on text
$('.smsAddressEmail').live({
	mouseenter: function() {
		var smsAddressID = getID(this);
		var is_active = $('#smsAddress' + smsAddressID).hasClass('smsAddressInactive');
		$(this).find('.text').hide();
		$(this).append('<span class=flag>' + (is_active ? 'Deactivate' : 'Activate') + '</span>');
	},
	mouseleave: function() {
		$(this).find('.flag').remove();
		$(this).find('.text').show();
	},
	click: function() {
		$(this).find('.flag').remove();
		var smsAddressID = getID(this);
		var smsAddress = $('#smsAddress' + smsAddressID);
		var is_active = smsAddress.hasClass('smsAddressInactive');
		post("${request.route_path('user_update')}", {
			token: token,
			smsAddressID: smsAddressID,
			smsAddressAction: is_active ? 'deactivate' : 'activate'
		}, function(data) {
			$('#smsAddressEmail' + smsAddressID).find('.text').show();
			if (data.isOk) {
				if (data.is_active) {
					smsAddress.removeClass('smsAddressInactive');
				} else {
					smsAddress.addClass('smsAddressInactive');
				}
			} else {
				alert(data.message);
			}
		});
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
		<td>
			<input id=save class=lockOnSave type=button value="${'Update' if user else 'Register'}" title='Send confirmation'>
		% if user:
			<input id=mutate type=button value=Mutate title='Invalidate other sessions for your security'>
		% endif
		</td>
		<td id=m_status class=message></td>
	</tr>
</table>
% if user:
	<p>
	For SMS alerts, send a text message to ${request.registry.settings['sms.email']} with 
	${user.id}-<span id=userCode>${user.code}</span> as the subject.
	</p>

	<div id=smsAddresses>
		<%include file='smsAddresses.mak'/>
	</div>
% endif
