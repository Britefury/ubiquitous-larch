function handleMessageFromServer(message) {
    var msg_type = message.msgtype;
    if (msg_type == "replace_fragment") {
        var frag_id = message.frag_id;
        var frag_content = message.frag_content;
        $("#"+frag_id).html(frag_content);
    }
    else {
        // Unreckognised message
        alert("Unreckognised message" + message);
    }
}

function handleMessagesFromServer(messages) {
    for (var i = 0; i < messages.length; i++) {
        handleMessageFromServer(messages[i]);
    }
}


function postEvent(src_element, event_name, event_data) {
    var elem = src_element.closest("span.__lch_event_elem");
    var element_id = elem.attr('id');

    var ev_msg = {
        msgtype: 'event',
        element_id: element_id,
        event_name: event_name,
        ev_data: event_data
    };

    var ev_json = JSON.stringify(ev_msg);

    var ev_data = {
        session_id: __larch_session_id,
        event_data: ev_json
    };

    $.ajax({
        type: 'POST',
        url: 'event',
        data: ev_data,
        success: function(msg) {
            handleMessagesFromServer(msg);
        },
        dataType: 'json'
    });
}


function aClicked(elem) {
    postEvent($(elem), "clicked", {});
}