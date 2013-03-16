//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************

__larch.__executeJS = function(js_code) {
    eval(js_code);
}




__larch.__buildConnectivity = function(segment) {
    // The state consists of the start and end nodes of a segment.
    // We often remove elements from the DOM in order to alter its contents.
    // Sometimes we put these nodes back in again. In such cases, the nextSibling attribute will be null,
    // preventing us from using it for iterating across the sequence of nodes.
    // So, we create a __lch_next attribute that points to the next sibling, so we can iterate using this instead.
    var p = null;
    for (var n = segment.start; n != segment.end; n = n.nextSibling) {
        if (p != null) {
            p.__lch_next = n;
        }
        p = n;
    }
    p.__lch_next = segment.end;
}

__larch.__clearConnectivity = function(nodes) {
    // Clear connectivity built earlier
    var p = null;
    for (var i = 0; i < nodes.length; i++)
    {
        var n = nodes[i];
        if (p != null) {
            p.__lch_next = null;
        }
        p = n;
    }
}


__larch.__newSegmentState = function(start, end) {
    // This creates a new 'segment state' to go into the segment table.
    return {'start': start, 'end': end}
}

__larch.__getNodesInActiveSegment = function(segment) {
    var nodeList = [];
    for (var n = segment.start; n != segment.end; n = n.nextSibling) {
        nodeList.push(n);
    }
    nodeList.push(segment.end);
    return nodeList;
}

__larch.__getNodesInInactiveSegment = function(segment) {
    // Iterate using __lch_next attribute; see __newSegmentState function for explanation
    var nodeList = [];
    var start = segment.start;
    if (start.hasOwnProperty('__lch_next')  &&  start.__lch_next !== null) {
        // This inactive segment was directly removed in a previous replacement operation.
        // We must use the __lch_next property to iterate.
        for (var n = segment.start; n != segment.end; n = n.__lch_next) {
            nodeList.push(n);
        }
    }
    else {
        // This segment was removed as a result of a parent being removed, hence __lch_next has
        // not been initialised. Iterate using nextSibling.
        for (var n = segment.start; n != segment.end; n = n.nextSibling) {
            nodeList.push(n);
        }
    }
    nodeList.push(segment.end);
    return nodeList;
}




__larch.__replaceSegment = function(oldSegmentState, newSegmentState) {
    var first = oldSegmentState.start;
    var parent = first.parentNode;

    // The nodes that we are about to remove from the DOM may be reused later.
    // Build out own connectivity structure so that we can iterate through them
    __larch.__buildConnectivity(oldSegmentState);

    var oldNodes = __larch.__getNodesInActiveSegment(oldSegmentState);
    var newNodes = __larch.__getNodesInActiveSegment(newSegmentState);

    newNodes.forEach(function(n) {parent.insertBefore(n, first);});
    oldNodes.forEach(function(n) {parent.removeChild(n);});
}


__larch.__replacePlaceholder = function(placeHolder, existingInactiveSegmentState) {
    var parent = placeHolder.parentNode;

    var newNodes = __larch.__getNodesInInactiveSegment(existingInactiveSegmentState);

    newNodes.forEach(function(n) {parent.insertBefore(n, placeHolder);});

    // These nodes are active: clear connectivity
    __larch.__clearConnectivity(newNodes);

    parent.removeChild(placeHolder);
}





__larch.__createSegmentContentNodesFromSource = function(content) {
    var elem = document.createElement("div");
    elem.innerHTML = content;
    return __larch.__newSegmentState(elem.firstChild, elem.lastChild);
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

__larch.__getSegmentBeginNodes = function() {
    return __larch.__getElementsOfClass("__lch_seg_begin", "span");
}

__larch.__executeInitialisers = function(initialisers) {
    var segment_table = __larch.__segment_table;
    for (var i = 0; i < initialisers.length; i++) {
        var x = initialisers[i];
        var segment_id = x[0];
        var inits = x[1];
        //console.log("Executing initialisers for " + segment_id);
        var state = segment_table[segment_id];
        if (state == undefined) {
            throw "Cannot get segment " + segment_id
        }
        var nodes = __larch.__getNodesInActiveSegment(state);
        for (var j = 1; j < nodes.length - 1; j++) {
            // The 'unused' variable node is referenced by the source code contained in the initialiser; it is needed by eval()
            var node = nodes[j];
            for (var k = 0; k < inits.length; k++) {
                eval(inits[k]);
            }
        }
    }
}

__larch.__register_segments = function() {
    var segment_table = __larch.__segment_table;

    var inlines = __larch.__getSegmentBeginNodes();

    for (var i = 0; i < inlines.length; i++) {
        // Get the start node and extract the segment ID
        var start = inlines[i];

        // Check if it is uninitialised
        if (!start.hasOwnProperty('__lch_initialised')) {
            start.__lch_initialised = true;

            // Extract the segment ID
            var segment_id = start.innerHTML;
            //console.log("Initialised " + segment_id);

            // Iterate forwards until we find the matching end node.
            var n = start;
            while (true) {
                // Set the node's segment ID
                n.__lch_seg_id = segment_id;

                if (n.getAttribute  &&  n.getAttribute("class") == '__lch_seg_end'  && n.innerHTML == segment_id) {
                    break;
                }

                // Next
                n = n.nextSibling;
            }

            // @n is now the end node
            var end = n;

            // Put an entry in our segment table
            segment_table[segment_id] = __larch.__newSegmentState(start, end);
        }
    }
}



__larch.__applyChanges = function(changes) {
    //console.log("STARTING UPDATE");
    var removed = changes.removed;
    var modified = changes.modified;
    var initialisers = changes.initialisers;

    var segment_table = __larch.__segment_table;

    // Handle removals
    for (var i = 0; i < removed.length; i++) {
        // Just remove them from the table
        // The DOM modifications will remove the nodes
        //console.log("Removed " + removed[i]);
        delete segment_table[removed[i]];
    }

    // Handle modifications
    for (var i = 0; i < modified.length; i++) {
        // Get the segment ID and content
        var segment_id = modified[i][0];
        var content = modified[i][1];

        var state = segment_table[segment_id];

        //console.log("Replaced " + segment_id);

        var newState = __larch.__createSegmentContentNodesFromSource(content);
        newState.start.__lch_initialised = true;

        // Unregister segment IDs
        var oldNodes = __larch.__getNodesInActiveSegment(state);
        oldNodes.forEach(function(n) {n.__lch_seg_id = null;});

        __larch.__replaceSegment(state, newState);

        // Register segment IDs
        var newNodes = __larch.__getNodesInActiveSegment(newState);
        newNodes.forEach(function(n) {n.__lch_seg_id = segment_id;});

        // Put in segment table
        segment_table[segment_id] = newState;
    }

    // Replace the placeholders with the segments that they reference
    var placeHolders = __larch.__getPlaceHolderNodes();
    // Replacing a placeholder may introduce content that contains yet more placeholders....
    while (placeHolders.length > 0) {
        for (var i = 0; i < placeHolders.length; i++) {
            // Get the placeholder node
            var p = placeHolders[i];
            // Extract the segment ID that if references
            var segment_id = p.innerHTML;

            // Get the segment that is to take its place
            var segment = segment_table[segment_id];

            // Replace it
            __larch.__replacePlaceholder(p, segment);
        }

        placeHolders = __larch.__getPlaceHolderNodes();
    }

    // Register any unregistered segments that have been introduced by modifications
    __larch.__register_segments();


    // Execute initialisers
    __larch.__executeInitialisers(initialisers);
    //console.log("FINISHED UPDATE");
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
                continue;
            }
            if (key.ctrlKey != undefined  &&  event.ctrlKey != key.ctrlKey) {
                continue;
            }
            if (key.shiftKey != undefined  &&  event.shiftKey != key.shiftKey) {
                continue;
            }
            if (key.metaKey != undefined  &&  event.metaKey != key.metaKey) {
                continue;
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
    }
    return undefined;
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



__larch.getSegmentIDForEvent = function(src_element) {
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

    return segment_id;
}

__larch.buildElementEventMessage = function(segment_id, event_name, event_data) {
    return {
        msgtype: 'event',
        segment_id: segment_id,
        event_name: event_name,
        ev_data: event_data
    };
}



__larch.sendEventMessagesToServer = function(ev_messages) {
    var ev_json = JSON.stringify(ev_messages);

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

__larch.postEventMessage = function(ev_msg) {
    var messages = [];

    if (__larch.eventFactoryQueue.length > 0) {
        // Create events from factory queue
        for (var i = 0; i < __larch.eventFactoryQueue.length; i++) {
            var key = __larch.eventFactoryQueue[i];
            var fac = __larch.eventFactoriesBySrcAndName[key];
            var ev_data = fac.event_factory();
            var msg = __larch.buildElementEventMessage(fac.segment_id, fac.event_name, ev_data);
            messages.push(msg);
        }
        // Clear factory queue
        __larch.eventFactoryQueue = [];
        __larch.eventFactoriesBySrcAndName = {};
    }

    // Add the message that we are posting
    messages.push(ev_msg);

    // Send
    __larch.sendEventMessagesToServer(messages);
}


__larch.postEvent = function(src_element, event_name, event_data) {
    var segment_id = __larch.getSegmentIDForEvent(src_element);

    if (segment_id != null) {
        var ev_msg = __larch.buildElementEventMessage(segment_id, event_name, event_data);
        __larch.postEventMessage(ev_msg);
    }
}


__larch.postDocumentEvent = function(event_name, event_data) {
    var ev_msg = {
        msgtype: 'event',
        segment_id: null,
        event_name: event_name,
        ev_data: event_data
    };

    __larch.postEventMessage(ev_msg);
}


__larch.eventFactoryQueue = [];
__larch.eventFactoriesBySrcAndName = {};


__larch.queueEventFactory = function(src_element, event_name, event_factory) {
    var segment_id = __larch.getSegmentIDForEvent(src_element);
    var key = segment_id + '__' + event_name;

    var fac = {segment_id: segment_id, event_name: event_name, event_factory: event_factory};
    if (!__larch.hasQueuedEventFactory(src_element, event_name)) {
        __larch.eventFactoryQueue.push(key);
    }
    __larch.eventFactoriesBySrcAndName[key] = fac;
}

__larch.hasQueuedEventFactory = function(src_element, event_name) {
    var segment_id = __larch.getSegmentIDForEvent(src_element);
    var key = segment_id + '__' + event_name;

    return __larch.eventFactoriesBySrcAndName.hasOwnProperty(key);
}


__larch.__onDocumentReady = function(initialisers) {
    __larch.__register_segments();
    __larch.__executeInitialisers(initialisers);
}

