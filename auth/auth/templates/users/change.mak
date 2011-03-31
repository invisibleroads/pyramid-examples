<%inherit file='/base.mako'/>

<%def name='title()'>Account ${'Registration' if c.isNew else 'Update'}</%def>

<%def name='css()'>
.field {width: 15em}
.inactive {color: gray}
</%def>

<%def name='js()'>
// Save descriptions
function getMessageObj(id) {
    return $('#m_' + id);
}
function showMessageByID(messageByID) {
    var focusSet = false;
    for (var i = 0; i < ids.length; i++) {
        var id = ids[i];
        var message = messageByID[id];
        var messageObj = getMessageObj(id);
        if (message) {
            messageObj.html('<b>' + message + '</b>');
            if (!focusSet) {
                $('#' + id).focus().select();
                focusSet = true;
            }
        } else {
            messageObj.html(defaultByID[id]);
        }
    }
}
var ids = ['username', 'password', 'nickname', 'email', 'status'];
var defaultByID = {};
for (var i = 0; i < ids.length; i++) {
    var id = ids[i];
    defaultByID[id] = getMessageObj(id).html();
}
// Define button behavior
function ajax_save() {
    var username = $('#username').val(),
        password = $('#password').val(), 
        nickname = $('#nickname').val(), 
        email = $('#email').val();
    $('.lockOnSave').attr('disabled', 'disabled');
    $.post("${h.url('person_register' if c.isNew else 'person_update')}", {
        username: username,
        password: password,
        nickname: nickname,
        email: email
    }, function(data) {
        var messageByID = {};
        if (data.isOk) {
            messageByID['status'] = "Please check your email to ${'create' if c.isNew else 'finalize changes to'} your account.";
        } else {
            $('.lockOnSave').removeAttr('disabled');
            messageByID = data.errorByID;
        }
        showMessageByID(messageByID);
    }, 'json');
}
$('#buttonSave').click(ajax_save);
$('.updateSMSAddress').click(function() {
    var button = $(this), action = button.val().toLowerCase(), smsAddressID = getNumber(this.id), smsAddressRow = $('#smsAddress' + smsAddressID), smsAddressEmail = $('#smsAddressEmail' + smsAddressID);
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
    $.post("${h.url('person_update')}", {smsAddressID: smsAddressID, action: action}, function(data) {
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
$('#email').keydown(function(e) {if (e.keyCode == 13) ajax_save()});
// Focus
$('#username').focus();
</%def>

<%def name="toolbar()">
${'Register for an account' if c.isNew else 'Update your account'}
</%def>

<%
from pylons import config
%>
<table>
    <tr>
        <td class=label><label for=username>Username</label></td>
        <td class=field><input id=username name=username class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_username>What you use to login</td>
    </tr>
    <tr>
        <td class=label><label for=password>Password</label></td>
        <td class=field><input id=password name=password class="lockOnSave maximumWidth" type=password autocomplete=off></td>
        <td id=m_password>So you have some privacy</td>
    </tr>
    <tr>
        <td class=label><label for=nickname>Nickname</label></td>
        <td class=field><input id=nickname name=nickname class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_nickname>How others see you</td>
    </tr>
    <tr>
        <td class=label><label for=email>Email</label></td>
        <td class=field><input id=email name=email class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_email>To confirm changes to your account</td>
    </tr>
    <tr>
        <td></td>
        <td><input id=buttonSave class=lockOnSave type=button value="${'Register' if c.isNew else 'Update'}"></td>
        <td id=m_status></td>
    </tr>
% if not c.isNew:
    <tr>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td colspan=3>Send ${h.getPersonID()} as a text message to ${config['sms.email']} for SMS alerts</td>
    </tr>
% for smsAddress in sorted(c.smsAddresses, key=lambda x: -x.is_active):
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
