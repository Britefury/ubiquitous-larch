//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************

__larch.__executeJS = function(js_code) {
    eval(js_code);
}


__larch.__replaceNode = function(before, after) {
    var parent = before.parentNode;
    parent.insertBefore(after, before);
    parent.removeChild(before);
}

__larch.__createElementFromSource = function(content) {
    var elem = document.createElement("div");
    elem.innerHTML = content;
    return elem.childNodes[0];
}

__larch.__getPlaceHolders = function() {
    if (document.getElementsByClassName) {
        return document.getElementsByClassName("__lch_placeholder");
    }
    else {
        var els = document.getElementsByTagName("span");
        var i = 0;
        var elem = null;
        var placeHolders = [];
        while (elem = els[i++]) {
            if (elem.className == "__lch_placeholder") {
                placeHolders.push(elem);
            }
        }
        return placeHolders;
    }
}

__larch.__applyChanges = function(changes) {
    var removed = changes.removed;
    var added = changes.added;
    var modified = changes.modified;

    var id_to_elem = __larch.__id_to_element_table;

    // Handle removals
    for (var i = 0; i < removed.length; i++) {
        delete id_to_elem[removed[o]];
    }

    // Handle additions
    for (var i = 0; i < added.length; i++) {
        var key = added[i][0];
        var content = added[i][1];

        id_to_elem[key] = {'elem': __larch.__createElementFromSource(content), 'in_document': false};
    }

    // Handle modifications
    for (var i = 0; i < modified.length; i++) {
        var key = modified[i][0];
        var content = modified[i][1];

        var state = id_to_elem[key];

        if (state.in_document) {
            var newElem = __larch.__createElementFromSource(content);
            __larch.__replaceNode(state.elem, newElem);
            state.elem = newElem;
        }
        else {
            state.elem = __larch.__createElementFromSource(content);
        }
    }

    // Handle the placeholders
    var placeHolders = __larch.__getPlaceHolders();
    while (placeHolders.length > 0) {
        for (var i = 0; i < placeHolders.length; i++) {
            var p = placeHolders[i];
            var key = p.innerHTML;

            var state = id_to_elem[key];
            state.in_document = true;
            __larch.__replaceNode(p, state.elem);
        }

        placeHolders = __larch.__getPlaceHolders();
    }

}

__larch.__handleMessageFromServer = function(message) {
    var msg_type = message.msgtype;
    if (msg_type == "modify_document") {
        var changes = message.changes;
        __larch.__applyChanges(changes);
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


__larch.postDocumentEvent = function(event_name, event_data) {
    var ev_msg = {
        msgtype: 'event',
        element_id: null,
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

