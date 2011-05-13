<%inherit file='/base.mak'/>

<%def name='title()'>Users</%def>

<%def name='css()'>
td {text-align: center}
.user {color: gray}
.user.is_active {color: black}
.flag {color: darkblue}
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
		{'sType': 'html'},
        {'sType': 'html'},
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
        var targetUserID = getID(this);
        var objText = $(this).find('.text').hide();
        var objRow = $('#user' + targetUserID);
        var message = objRow.hasClass('is_super') ? 'Demote' : 'Promote';
		$(this).append('<span class=flag>' + message + '</span>');
	},
	mouseleave: function() {
		$(this).find('.flag').remove();
        $(this).find('.text').show();
	},
    click: function() {
        var targetUserID = getID(this);
        var objFlag = $(this).find('.flag').remove();
        var objText = $(this).find('.text').show();
        var objRow = $('#user' + targetUserID);
        var is_super = objRow.hasClass('is_super') ? 0 : 1;
        if (confirm((is_super ? 'Demote from' : 'Promote to') + ' superuser?')) {
            objText.text(is_super ? 'Superuser' : '');
            if (is_super) {
                objRow.addClass('is_super');
            } else {
                objRow.removeClass('is_super');
            }
            post("${request.route_path('user_move')}", {
                token: token,
                targetUserID: targetUserID,
                is_super: is_super
            }, function(data) {
                if (!data.isOk) {
                    objText.text(is_super ? '' : 'Superuser');
                    if (is_super) {
                        objRow.removeClass('is_super');
                    } else {
                        objRow.addClass('is_super');
                    }
                    alert(data.message);
                }
            });
        }
    }
});
$('.when_login').live({
	mouseenter: function() {
        var targetUserID = getID(this);
        var objText = $(this).find('.text').hide();
        var objRow = $('#user' + targetUserID);
        var message = objRow.hasClass('is_active') ? 'Deactivate' : 'Activate';
		$(this).append('<span class=flag>' + message + '</span>');
	},
	mouseleave: function() {
		$(this).find('.flag').remove();
        $(this).find('.text').show();
	},
    click: function() {
        var targetUserID = getID(this);
        var objFlag = $(this).find('.flag').remove();
        var objText = $(this).find('.text').show();
        var objRow = $('#user' + targetUserID);
        var is_active = objRow.hasClass('is_active') ? 0 : 1;
        if (confirm((is_active ? 'Activate' : 'Deactivate') + ' user?')) {
            if (is_active) {
                objRow.addClass('is_active');
            } else {
                objRow.removeClass('is_active');
            }
            post("${request.route_path('user_move')}", {
                token: token,
                targetUserID: targetUserID,
                is_active: is_active
            }, function(data) {
                if (!data.isOk) {
                    if (is_active) {
                        objRow.removeClass('is_active');
                    } else {
                        objRow.addClass('is_active');
                    }
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
		<tr id=user${userID} class='user \
        % if user.is_active:
            is_active\
        % endif
        % if user.is_super:
            is_super\
        % endif
        '>
			<td>${user.nickname}</td>
            <td id=role${userID}
            % if USER_ID != userID:
            class=role
            % endif
            >
                <span class=text>\
                % if user.is_super:
                    Superuser\
                % endif
                </span>
            </td>
			<td id=when_login${userID}
            % if USER_ID != userID:
            class=when_login
            % endif
            >
			% if user.when_login:
				<%
				when_login = user.when_login
				localWhenIO = whenIO.WhenIO(user.minutes_offset)
				%>
				<span class=text title="${when_login.strftime('%Y%m%d%H%M%S')}"></span>
				${localWhenIO.format(when_login)} ${localWhenIO.format_offset()}
			% else:
				<span class=text title=''></span>
			% endif
			</td>
		</tr>
	% endfor
	</tbody>
</table>
