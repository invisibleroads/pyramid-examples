<%inherit file='/base.mak'/>

<%def name='title()'>Login</%def>

<%def name='css()'>
#resetPack {display: none}
#resetForm {display: none}
</%def>

<%def name='toolbar()'>
## <a class='hover link off' href="${request.route_path('user_register')}">Register for an account</a>
</%def>

<%def name='root()'>
<script src="${request.static_url('auth:static/recaptcha_ajax.js')}"></script>
</%def>

<%def name='js()'>
// Define global variables
var rejection_count = 0;

// Define functions
function isEmpty(inputID) {
    var input = $('#' + inputID), output = $('#m_' + inputID);
    if (input.val() == '') {
        output.text('You must provide a ' + inputID);
        input.focus();
        return 1;
    } else {
        output.text('');
        return 0;
    }
}
function login() {
    // Validate
    var errorCount = 0;
    errorCount = errorCount + isEmpty('username');
    errorCount = errorCount + isEmpty('password');
    if (errorCount) {
        $('#resetPack').hide();
        return;
    }
    // Initialize
    var loginData = {
        'username': $('#username').val(),
        'password': $('#password').val(),
        'offset': $('#offset').val()
    }
    // Get recaptcha
    if ($('#recaptcha_challenge_field').length) {
        loginData['recaptcha_challenge'] = $('#recaptcha_challenge_field').val();
        loginData['recaptcha_response'] = $('#recaptcha_response_field').val();
    }
    // Attempt login
    $.post("${request.route_path('user_login')}", loginData, function(data) {
        if (data.isOk) {
            window.location = "${url}";
        } else {
            // Give feedback
            $('#resetPack').show();
            $('#resetLink').show();
            $('#resetForm').hide();
            // Update rejection count
            rejection_count = data.rejection_count ? data.rejection_count : rejection_count + 1;
            // If there have been too many rejections,
            if (rejection_count >= ${REJECTION_LIMIT}) {
                Recaptcha.create("${request.registry.settings.get('recaptcha.public', '')}", 'recaptcha', {
                    theme: 'red',
                    callback: Recaptcha.focus_response_field
                });
            }
        }
    });
}
<%doc>
function reset() {
    // Check that the email is not empty
    var email = $.trim($('#resetEmail').val());
    if (!email) {
        $('#resetEmail').focus();
        return;
    }
    // Post
    $('.lockOnReset').attr('disabled', true);
    $.post("${request.route_path('user_reset')}", {
        'email': email
    }, function(data) {
        if (data.isOk) {
            $('#m_password').html('Please check your mailbox');
        } else {
            $('#m_password').html('Email not found');
            $('.lockOnReset').removeAttr('disabled');
        }
    });
}

// Prepare reset form
$('#resetLink').click(function() {
    $('#resetLink').hide();
    $('#resetForm').show();
    $('#resetEmail').val('').keydown(function(e) {if (e.keyCode == 13) reset()}).focus();
});
$('#reset').click(reset);
</%doc>

// Prepare login form
$('#login').click(login);
$('#username').keydown(function(e) {if (e.keyCode == 13) $('#password').focus()});
$('#password').keydown(function(e) {if (e.keyCode == 13) login()});

// Configure
$('#offset').val(new Date().getTimezoneOffset());
$('#username').focus();
</%def>

<table>
	<tr>
		<td><label for=username>Username</label></td>
		<td><input id=username></td>
		<td>
			<span id=m_username>
				## ${'. '.join(request.session.pop_flash())}
			</span>
			<span id=resetPack>
				<a id=resetLink class='hover link off'>Did you forget your login?</a>
				<span id=resetForm>
					Email
					<input class=lockOnReset id=resetEmail>
					<input class=lockOnReset id=reset type=button value=Reset>
				</span>
			</span>
		</td>
	</tr>
	<tr>
		<td><label for=password>Password</label></td>
		<td><input id=password type=password></td>
		<td id=m_password></td>
	</tr>
	<tr>
		<td><label for=offset>Time</label</td>
		<td>
			<select id=offset>
				<%include file='offsets.mak'/>
			</select>
		</td>
		<td id=m_offset></td>
	</tr>
</table>
<div id=recaptcha></div>
<input id=login type=button value=Login><br>
<br>
<a href='/docs' class='hover link off'>Read documentation for ${SITE_NAME} ${SITE_VERSION}</a>
