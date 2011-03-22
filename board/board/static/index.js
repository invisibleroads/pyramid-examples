function add() {
    // Get text
    var text = $.trim($('#text').val());
    // Exit if the text is empty
    if (text.length == 0) {
        $('#text').focus();
        return;
    }
    // Add post
    $.post("${request.route_url('add')}", {
        text: text
    }, function(data) {
        $('#posts').html(data);
        $('#text').val('');
    });
}
$('#add').click(add);
$('#text').keydown(function(e) {
    if (e.keyCode == 13) add();
}).focus();
