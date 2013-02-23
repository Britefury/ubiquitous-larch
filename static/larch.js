//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************

__larch.__executeJS = function(js_code) {
    eval(js_code);
}


__larch.__iterateThroughStateWithoutMutations = function(state, fn) {
    var n = state.start;
    while (n != state.end) {
        var next = n.nextSibling;
        fn(n);
        n = next;
    }
    fn(n);
}

__larch.__getNodesInState = function(state) {
    var nodeList = [];
    for (var n = state.start; n != state.end; n = n.nextSibling) {
        nodeList.push(n);
    }
    nodeList.push(state.end);
    return nodeList;
}


__larch.__replaceNodeRange = function(oldState, newState) {
    var first = oldState.start;
    var parent = first.parentNode;

    var oldNodes = __larch.__getNodesInState(oldState);
    var newNodes = __larch.__getNodesInState(newState);

    for (var i = 0; i < newNodes.length; i++) {
        parent.insertBefore(newNodes[i], first);
    }

    for (var i = 0; i < oldNodes.length; i++) {
        parent.removeChild(oldNodes[i]);
    }
}

__larch.__replacePlaceholder = function(placeHolder, newState) {
    var parent = placeHolder.parentNode;

    var newNodes = __larch.__getNodesInState(newState);

    for (var i = 0; i < newNodes.length; i++) {
        parent.insertBefore(newNodes[i], placeHolder);
    }

    parent.removeChild(placeHolder);
}

__larch.__isSegmentNode = function(node) {
    if (node.className) {
        var c = node.className;
        if (c == "__lch_seg_placeholder"  ||  c == "__lch_seg_inline_begin"  ||  c == "__lch_seg_inline_end") {
            return true;
        }
    }
    return false;
}

__larch.__createSegmentContentNodesFromSource = function(content) {
    var elem = document.createElement("div");
    elem.innerHTML = content;
    return {'start': elem.firstChild, 'end': elem.lastChild};
}

__larch.__getElementsOfClass = function(className, tagName) {
    if (document.getElementsByClassName) {
        return document.getElementsByClassName(className);
    }
    else {
        // IE does not support getElementsByClassName
        var els = document.getElementsByTagName(tagName);
        var i = 0;
        var elem = null;
        var placeHolders = [];
        while (elem = els[i++]) {
            if (elem.className == className) {
                placeHolders.push(elem);
            }
        }
        return placeHolders;
    }
}

__larch.__getPlaceHolderNodes = function() {
    return __larch.__getElementsOfClass("__lch_seg_placeholder", "span");
}

__larch.__getInlineBeginNodes = function() {
    return __larch.__getElementsOfClass("__lch_seg_inline_begin", "span");
}

__larch.__executeInitialisers = function(initialisers) {
    var segment_table = __larch.__segment_table;
    for (var i = 0; i < initialisers.length; i++) {
        var x = initialisers[i];
        var segment_id = x[0];
        var inits = x[1];
        var state = segment_table[segment_id];
        var nodes = __larch.__getNodesInState(state);
        for (var j = 0; j < nodes.length; j++) {
            // The 'unused' variable node is referenced by the source code contained in the initialiser; it is needed by eval()
            var node = nodes[j];
            for (var k = 0; k < inits.length; k++) {
                eval(inits[k]);
            }
        }
    }
}

__larch.__handleInlineNodes = function() {
    var segment_table = __larch.__segment_table;

    var inlines = __larch.__getInlineBeginNodes();

    // Take a copy of the node list, since we are about the mutate the DOM
    var inlineNodes = [];
    for (var i = 0; i < inlines.length; i++) {
        inlineNodes.push(inlines[i]);
    }
    for (var i = 0; i < inlineNodes.length; i++) {
        // Get the start node and extract the segment ID
        var start = inlineNodes[i];
        var segment_id = start.innerHTML;

        // Iterate forwards until we find the matching end node.
        var n = start;
        while (true) {
            // Set the node's segment ID
            n.__lch_seg_id = segment_id;

            if (n.getAttribute  &&  n.getAttribute("class") == '__lch_seg_inline_end'  && n.innerHTML == segment_id) {
                break;
            }

            // Next
            n = n.nextSibling;
        }

        // @n is now the end node
        var end = n;

        // Get the parent
        var parent = start.parentNode;

        // Put an entry in our segment table
        segment_table[segment_id] = {'start': start, 'end': end};
    }
}



__larch.__applyChanges = function(changes) {
    var removed = changes.removed;
    var added = changes.added;
    var modified = changes.modified;
    var initialisers = changes.initialisers;

    var segment_table = __larch.__segment_table;

    // Handle removals
    for (var i = 0; i < removed.length; i++) {
        // Just remove them from the table
        // The DOM modifications will remove the nodes
        delete segment_table[removed[i]];
    }

    // Handle additions
    /*for (var i = 0; i < added.length; i++) {
        var segment_id = added[i][0];
        var content = added[i][1];

        id_to_elem[key] = {'nodes': __larch.__createSegmentContentNodesFromSource(content, segment_id, initialisers)};
    }*/

    // Handle modifications
    for (var i = 0; i < modified.length; i++) {
        // Get the segment ID and content
        var segment_id = modified[i][0];
        var content = modified[i][1];

        var state = segment_table[segment_id];

        var newState = __larch.__createSegmentContentNodesFromSource(content);

        // Unregister segment IDs
        __larch.__iterateThroughStateWithoutMutations(state, function(n) {n.__lch_seg_id = null; } );

        __larch.__replaceNodeRange(state, newState);

        // Register segment IDs
        __larch.__iterateThroughStateWithoutMutations(newState, function(n) {n.__lch_seg_id = segment_id; } );
    }

    // Handle the placeholders
    var placeHolders = __larch.__getPlaceHolderNodes();
    while (placeHolders.length > 0) {
        for (var i = 0; i < placeHolders.length; i++) {
            var p = placeHolders[i];
            var segment_id = p.innerHTML;

            var state = segment_table[segment_id];
            __larch.__replacePlaceholder(p, state);
        }

        placeHolders = __larch.__getPlaceHolderNodes();
    }

    // Handle the inline elements
    __larch.__handleInlineNodes();


    // Handle initialisers
    __larch.__executeInitialisers(initialisers);
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
        __larch.postEvent(event.target, 'keydown', k);
    }
}

__larch.__onkeyup = function(event, keys) {
    var k = __larch.__handleKeyEvent(event, keys);
    if (k != undefined) {
        __larch.postEvent(event.target, 'keyup', k);
    }
}

__larch.__onkeypress = function(event, keys) {
    var k = __larch.__handleKeyEvent(event, keys);
    if (k != undefined) {
        __larch.postEvent(event.target, 'keypress', k);
    }
}


__larch.postEvent = function(src_element, event_name, event_data) {
    var n = src_element;
    var segment_id = null;
    while (n != null) {
        if (n.__lch_seg_id) {
            // We have a segment ID
            segment_id = n.__lch_seg_id;
            break;
        }
        n = n.parentNode;
    }

    if (segment_id != null) {
        var ev_msg = {
            msgtype: 'event',
            segment_id: segment_id,
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


__larch.__onDocumentReady = function(initialisers) {
    __larch.__handleInlineNodes();
    __larch.__executeInitialisers(initialisers);
}

