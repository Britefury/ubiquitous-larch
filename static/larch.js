//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************

__larch.__executeJS = function(js_code) {
    eval(js_code);
}


__larch.__replaceNodes = function(oldNodeList, newNodeList) {
    var first = oldNodeList[0];
    var parent = first.parentNode;

    for (var i = 0; i < newNodeList.length; i++) {
        parent.insertBefore(newNodeList[i], first);
    }
    for (var i = 0; i < oldNodeList.length; i++) {
        parent.removeChild(oldNodeList[i]);
    }
//    var children = Array.prototype.slice.call(parent.childNodes, 0, parent.childNodes.length);
//    var i = children.indexOf(first);
//    var j = children.indexOf(oldNodeList[oldNodeList.length-1])+1;
//    //children.splice.apply(children, [i,j-i].concat(newNodeList));
//    Array.prototype.splice.apply(parent.childNodes, [i,j-i].concat(newNodeList));
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
    var nodes = elem.childNodes;
    var newNodes = [];
    for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        if (__larch.__isSegmentNode(n)) {
            continue;
        }
        newNodes.push(n);
    }
    return newNodes;
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
        var nodes = state.nodes;
        for (var j = 0; j < nodes.length; j++) {
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

        // The list of nodes in this segment
        var nodeRange = [];

        // Iterate forwards until we find the matching end node. Accumulate only inner nodes into @nodeRange
        var n = start.nextSibling;
        while (true) {
            if (n.getAttribute  &&  n.getAttribute("class") == '__lch_seg_inline_end'  && n.innerHTML == segment_id) {
                break;
            }
            if (!__larch.__isSegmentNode(n)) {
                nodeRange.push(n);
                n.__lch_seg_id = segment_id;
            }
            n = n.nextSibling;
        }

        // @n is now the end node

        // Get the parent
        var parent = start.parentNode;

        // In the case of an empty segment, add an empty span element in between, so that we have a node to reference
        // in the future.
        if (nodeRange.length == 0) {
            // No nodes within the guards; create an empty span
            var s = document.createElement("span");
            s.__lch_seg_id = segment_id;
            parent.insertBefore(s, n);
            nodeRange.push(s);
        }

        // Remove the start and end span nodes
        parent.removeChild(start);
        parent.removeChild(n);

        // Put an entry in our segment table
        segment_table[segment_id] = {'nodes': nodeRange};
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

        var newNodes = __larch.__createSegmentContentNodesFromSource(content);

        // Unregister segment IDs
        for (var j = 0; j < state.nodes.length; j++) {
            state.nodes[j].__lch_seg_id = null;
        }

        __larch.__replaceNodes(state.nodes, newNodes);
        state.nodes = newNodes;

        // Register segment IDs
        for (var j = 0; j < newNodes.length; j++) {
            newNodes[j].__lch_seg_id = segment_id;
        }
    }

    // Handle the placeholders
    var placeHolders = __larch.__getPlaceHolderNodes();
    while (placeHolders.length > 0) {
        for (var i = 0; i < placeHolders.length; i++) {
            var p = placeHolders[i];
            var segment_id = p.innerHTML;

            var state = segment_table[segment_id];
            __larch.__replaceNodes([p], state.nodes);
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

