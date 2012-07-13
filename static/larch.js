//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************

__larch.__executeJS = function(js_code) {
    eval(js_code);
}

__larch.__handleMessageFromServer = function(message) {
    var msg_type = message.msgtype;
    if (msg_type == "replace_fragment") {
        var frag_id = message.frag_id;
        var frag_content = message.frag_content;
        var fragment_element = document.getElementById(frag_id);
        fragment_element.innerHTML = frag_content;
    }
    else if (msg_type == "execute_js") {
        var js_code = message.js_code;
        __larch.__executeJS(js_code);
    }
    else {
        // Unreckognised message
        throw ('Larch: unrecognised message" + message');
    }
}

__larch.__handleMessagesFromServer = function(messages) {
    for (var i = 0; i < messages.length; i++) {
        __larch.__handleMessageFromServer(messages[i]);
    }
}



__larch.__handleKeyEvent = function(event, keys) {
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (key.keyCode == undefined  ||  event.keyCode == key.keyCode) {
            if (key.altKey != undefined  &&  event.altKey != key.altKey) {
                break;
            }
            if (key.ctrlKey != undefined  &&  event.ctrlKey != key.ctrlKey) {
                break;
            }
            if (key.shiftKey != undefined  &&  event.shiftKey != key.shiftKey) {
                break;
            }
            if (key.metaKey != undefined  &&  event.metaKey != key.metaKey) {
                break;
            }
            // We have a match
            var k = {};
            k.keyCode = event.keyCode;
            k.altKey = event.altKey;
            k.ctrlKey = event.ctrlKey;
            k.shiftKey = event.shiftKey;
            k.metaKey = event.metaKey;
            return k;
        }
        return undefined;
    }
}

__larch.__onkeydown = function(event, keys) {
    var k = __larch.__handleKeyEvent(event, keys);
    if (k != undefined) {
        __larch.postEvent($(event.target), 'keydown', k);
    }
}

__larch.__onkeyup = function(event, keys) {
    var k = __larch.__handleKeyEvent(event, keys);
    if (k != undefined) {
        __larch.postEvent($(event.target), 'keyup', k);
    }
}

__larch.__onkeypress = function(event, keys) {
    var k = __larch.__handleKeyEvent(event, keys);
    if (k != undefined) {
        __larch.postEvent($(event.target), 'keypress', k);
    }
}


__larch.postEvent = function(src_element, event_name, event_data) {
    var elem = $(src_element).closest("span.__lch_event_elem");
    var element_id = elem.attr('id');

    var ev_msg = {
        msgtype: 'event',
        element_id: element_id,
        event_name: event_name,
        ev_data: event_data
    };

    var ev_json = JSON.stringify(ev_msg);

    var ev_data = {
        session_id: __larch.__session_id,
        event_data: ev_json
    };

    $.ajax({
        type: 'POST',
        url: 'event',
        data: ev_data,
        success: function(msg) {
            __larch.__handleMessagesFromServer(msg);
        },
        dataType: 'json'
    });
}

