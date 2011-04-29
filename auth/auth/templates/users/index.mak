<%inherit file='/base.mak'/>

<%def name='title()'>Users</%def>

<%def name='css()'>
td {text-align: center}
.flag {font-size: xx-small; vertical-align: middle}
</%def>

<%def name='toolbar()'>
${len(users)} users
</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('auth:static/dataTables/style.css')}">
<script src="${request.static_url('auth:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('auth:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
function computeTableHeight() {
	return $(window).height() - 100;
}
var usersTable = $('#users').dataTable({
	'aaSorting': [[2, 'desc']],
	'aoColumns': [
		{'sType': 'string'},
        {'sType': 'string'},
		{'sType': 'title-string'}
	],
	'bInfo': false,
	'bPaginate': false,
	'oLanguage': {'sSearch': 'Filter'},
	'sScrollY': computeTableHeight()
});
$(window).bind('resize', function() {
	$('.dataTables_scrollBody').height(computeTableHeight());
	usersTable.fnAdjustColumnSizing();
});
$('.dataTables_filter input').focus();
% if IS_SUPER:
var token = '${request.session.get_csrf_token()}';
$('.role').live({
	mouseenter: function() {
        var objText = $(this).find('.text').hide();
        var message = $.trim(objText.text()) ? 'Demote' : 'Promote';
		$(this).append('<span class=flag>' + message + '</span>');
	},
	mouseleave: function() {
		$(this).find('.flag').remove();
        $(this).find('.text').show();
	},
    click: function() {
        var objFlag = $(this).find('.flag').remove();
        var objText = $(this).find('.text').show();
        var message, is_super;
        if ($.trim(objText.text())) {
            message = 'Demote from'
            is_super = 0;
        } else {
            message = 'Promote to'
            is_super = 1;
        }
        if (confirm(message + ' superuser?')) {
            objText.text(is_super ? 'Superuser' : '');
            post("${request.route_path('user_move')}", {
                token: token,
                targetUserID: getID(this),
                is_super: is_super
            }, function(data) {
                if (!data.isOk) {
                    objText.text(is_super ? '' : 'Superuser');
                    alert(data.message);
                }
            });
        }
    }
});
% endif
</%def>

<%!
import whenIO
%>

<table id=users>
	<thead>
		<tr>
			<th>Nickname</th>
            <th>Role</th>
			<th>Last Login</th>
		</tr>
	</thead>
	<tbody>
	% for user in users:
        <%
        userID = user.id;
        %>
		<tr>
			<td>${user.nickname}</td>
            <td 
            % if USER_ID != userID:
            class=role
            % endif
            id=role${userID}>
                <span class=text>\
                % if user.is_super:
                    Superuser\
                % endif
                </span>
            </td>
			<td>
			% if user.when_login:
				<%
				when_login = user.when_login
				localWhenIO = whenIO.WhenIO(user.offset)
				%>
				<span title="${when_login.strftime('%Y%m%d%H%M%S')}"></span>
				${localWhenIO.format(when_login)} ${localWhenIO.format_offset()}
			% else:
				<span title=''></span>
			% endif
			</td>
		</tr>
	% endfor
	</tbody>
</table>
