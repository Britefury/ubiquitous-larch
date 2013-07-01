//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2012.
//-*************************
larch.controls = {};


larch.__executeJS = function(js_code) {
    try {
        eval(js_code);
    }
    catch (e) {
        console.log("Dynamic JS code execution: caught " + e + " when executing " + code);
    }
};

larch.__addDependency = function(dep) {
    $(dep).appendTo("head");
};




larch.__buildConnectivity = function(segment) {
    // The state consists of the start and end nodes of a segment.
    // We often remove elements from the DOM in order to alter its contents.
    // Sometimes we put these nodes back in again. In such cases, the nextSibling attribute will be null,
    // preventing us from using it for iterating across the sequence of nodes.
    // So, we create a __lch_next attribute that points to the next sibling, so we can iterate using this instead.
    var p = null;
    for (var n = segment.start; n !== segment.end; n = n.nextSibling) {
        if (p !== null) {
            p.__lch_next = n;
        }
        p = n;
    }
    p.__lch_next = segment.end;
};

larch.__clearConnectivity = function(nodes) {
    // Clear connectivity built earlier
    var p = null;
    for (var i = 0; i < nodes.length; i++)
    {
        var n = nodes[i];
        if (p !== null) {
            p.__lch_next = null;
        }
        p = n;
    }
};


larch.__newSegmentState = function(start, end) {
    // This creates a new 'segment state' to go into the segment table.
    return {'start': start, 'end': end}
};

larch.__getNodesInActiveSegment = function(segment) {
    var nodeList = [];
    for (var n = segment.start; n !== segment.end; n = n.nextSibling) {
        nodeList.push(n);
    }
    nodeList.push(segment.end);
    return nodeList;
};

larch.__getNodesInInactiveSegment = function(segment) {
    // Iterate using __lch_next attribute; see __newSegmentState function for explanation
    var nodeList = [];
    var start = segment.start;
    if (start.hasOwnProperty('__lch_next')  &&  start.__lch_next !== null) {
        // This inactive segment was directly removed in a previous replacement operation.
        // We must use the __lch_next property to iterate.
        for (var n = segment.start; n !== segment.end; n = n.__lch_next) {
            nodeList.push(n);
        }
    }
    else {
        // This segment was removed as a result of a parent being removed, hence __lch_next has
        // not been initialised. Iterate using nextSibling.
        for (var n = segment.start; n !== segment.end; n = n.nextSibling) {
            nodeList.push(n);
        }
    }
    nodeList.push(segment.end);
    return nodeList;
};




larch.__replaceSegment = function(oldSegmentState, newSegmentState) {
    var first = oldSegmentState.start;
    var parent = first.parentNode;

    // The nodes that we are about to remove from the DOM may be reused later.
    // Build out own connectivity structure so that we can iterate through them
    larch.__buildConnectivity(oldSegmentState);

    var oldNodes = larch.__getNodesInActiveSegment(oldSegmentState);
    var newNodes = larch.__getNodesInActiveSegment(newSegmentState);

    newNodes.forEach(function(n) {parent.insertBefore(n, first);});
    oldNodes.forEach(function(n) {parent.removeChild(n);});
};


larch.__replacePlaceholder = function(placeHolder, existingInactiveSegmentState) {
    var parent = placeHolder.parentNode;

    var newNodes = larch.__getNodesInInactiveSegment(existingInactiveSegmentState);

    newNodes.forEach(function(n) {parent.insertBefore(n, placeHolder);});

    // These nodes are active: clear connectivity
    larch.__clearConnectivity(newNodes);

    parent.removeChild(placeHolder);
};





larch.__createSegmentContentNodesFromSource = function(content) {
    var elem = document.createElement("div");
    elem.innerHTML = content;
    return larch.__newSegmentState(elem.firstChild, elem.lastChild);
};



larch.__getElementsOfClass = function(className, tagName) {
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
            if (elem.className === className) {
                placeHolders.push(elem);
            }
        }
        return placeHolders;
    }
};

larch.__getPlaceHolderNodes = function() {
    return larch.__getElementsOfClass("__lch_seg_placeholder", "span");
};

larch.__getSegmentBeginNodes = function() {
    return larch.__getElementsOfClass("__lch_seg_begin", "span");
};

larch.__executeNodeScripts = function(node_scripts) {
    var segment_table = larch.__segment_table;
    for (var i = 0; i < node_scripts.length; i++) {
        var node_scipt = node_scripts[i];
        var segment_id = node_scipt[0];
        var script = node_scipt[1];
        //console.log("Executing initialisers for " + segment_id);
        var state = segment_table[segment_id];
        if (state === undefined) {
            throw "Cannot get segment " + segment_id
        }
        var nodes = larch.__getNodesInActiveSegment(state);
        for (var j = 1; j < nodes.length - 1; j++) {
            // The 'unused' variable node is referenced by the source code contained in the initialiser; it is needed by eval()
            var node = nodes[j];        // <<-- DO NOT DELETE
            for (var k = 0; k < script.length; k++) {
                try {
                    eval(script[k]);
                }
                catch (e) {
                    console.log("Executing initialisers: caught " + e + " when executing " + script[k]);
                }
            }
        }
    }
};

larch.__register_segments = function() {
    var segment_table = larch.__segment_table;

    var inlines = larch.__getSegmentBeginNodes();

    for (var i = 0; i < inlines.length; i++) {
        // Get the start node and extract the segment ID
        var start = inlines[i];

        // Check if it is uninitialised
        if (!start.hasOwnProperty('__lch_initialised')) {
            start.__lch_initialised = true;

            // Extract the segment ID
            var segment_id = start.getAttribute("data-larchsegid");
            //console.log("Initialised " + segment_id);

            // Iterate forwards until we find the matching end node.
            var n = start;
            while (true) {
                // Set the node's segment ID
                n.__lch_seg_id = segment_id;

                if (n.getAttribute  &&  n.getAttribute("class") === '__lch_seg_end'  && n.getAttribute("data-larchsegid") === segment_id) {
                    break;
                }

                // Next
                var nextNode = n.nextSibling;
                if (nextNode === null) {
                    throw "Did not find matching segment end node";
                }
                n = nextNode;
            }

            // @n is now the end node
            var end = n;

            // Put an entry in our segment table
            segment_table[segment_id] = larch.__newSegmentState(start, end);
        }
    }
};



larch.__applyChanges = function(changes) {
    //console.log("STARTING UPDATE");
    var removed = changes.removed;
    var modified = changes.modified;
    var initialise_scripts = changes.initialise_scripts;
    var shutdown_scripts = changes.shutdown_scripts;

    var segment_table = larch.__segment_table;

    // Execute shutdown scripts
    larch.__executeNodeScripts(shutdown_scripts);

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

        var newState = larch.__createSegmentContentNodesFromSource(content);
        newState.start.__lch_initialised = true;

        // Unregister segment IDs
        var oldNodes = larch.__getNodesInActiveSegment(state);
        oldNodes.forEach(function(n) {n.__lch_seg_id = null;});

        larch.__replaceSegment(state, newState);

        // Register segment IDs
        var newNodes = larch.__getNodesInActiveSegment(newState);
        newNodes.forEach(function(n) {n.__lch_seg_id = segment_id;});

        // Put in segment table
        segment_table[segment_id] = newState;
    }

    // Replace the placeholders with the segments that they reference
    var placeHolders = larch.__getPlaceHolderNodes();
    // Replacing a placeholder may introduce content that contains yet more placeholders....
    while (placeHolders.length > 0) {
        for (var i = 0; i < placeHolders.length; i++) {
            // Get the placeholder node
            var p = placeHolders[i];
            // Extract the segment ID that if references
            var segment_id = p.getAttribute("data-larchsegid");

            // Get the segment that is to take its place
            var segment = segment_table[segment_id];

            // Replace it
            larch.__replacePlaceholder(p, segment);
        }

        placeHolders = larch.__getPlaceHolderNodes();
    }

    // Register any unregistered segments that have been introduced by modifications
    larch.__register_segments();


    // Execute initialise scripts
    larch.__executeNodeScripts(initialise_scripts);
    //console.log("FINISHED UPDATE");
};

larch.__handleMessageFromServer = function(message) {
    var msg_type = message.msgtype;
    if (msg_type === "modify_document") {
        var changes = message.changes;
        larch.__applyChanges(changes);
    }
    else if (msg_type === "execute_js") {
        var js_code = message.js_code;
        larch.__executeJS(js_code);
    }
    else if (msg_type === "add_dependencies") {
        var deps = message.deps;
        for (var i = 0; i < deps.length; i++) {
            larch.__addDependency(deps[i]);
        }
    }
    else if (msg_type === "resources_modified") {
        var resource_ids = message.resource_ids;
        for (var i = 0; i < resource_ids.length; i++) {
            larch.__resourceModified(resource_ids[i]);
        }
    }
    else if (msg_type === "resources_disposed") {
        var resource_ids = message.resource_ids;
        for (var i = 0; i < resource_ids.length; i++) {
            larch.__destroyResource(resource_ids[i]);
        }
    }
    else {
        // Unreckognised message
        throw ('Larch: unrecognised message" + message');
    }
};

larch.__handleMessagesFromServer = function(messages) {
    for (var i = 0; i < messages.length; i++) {
        larch.__handleMessageFromServer(messages[i]);
    }
};



larch.__matchKeyEvent = function(event, key) {
    if (key.keyCode === undefined  ||  event.keyCode == key.keyCode) {
        if (key.altKey !== undefined  &&  event.altKey != key.altKey) {
            return false;
        }
        if (key.ctrlKey !== undefined  &&  event.ctrlKey != key.ctrlKey) {
            return false;
        }
        if (key.shiftKey !== undefined  &&  event.shiftKey != key.shiftKey) {
            return false;
        }
        if (key.metaKey !== undefined  &&  event.metaKey != key.metaKey) {
            return false;
        }
        return true;
    }
    return false;
};

larch.__eventToKey = function(event) {
    return {
        keyCode: event.keyCode,
        altKey: event.altKey,
        ctrlKey: event.ctrlKey,
        shiftKey: event.shiftKey,
        metaKey: event.metaKey
    };
};

larch.__handleKeyEvent = function(event, keys) {
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (larch.__matchKeyEvent(event, key)) {
            // We have a match
            var k = larch.__eventToKey(event);
            return [k, key.preventDefault];
        }
    }
    return undefined;
};

larch.__onkeydown = function(event, keys) {
    var k = larch.__handleKeyEvent(event, keys);
    if (k !== undefined) {
        larch.postEvent(event.target, 'keydown', k[0]);
        if (k[1] === 1) {
            event.preventDefault();
            return false;
        }
    }
    return true;
};

larch.__onkeyup = function(event, keys) {
    var k = larch.__handleKeyEvent(event, keys);
    if (k !== undefined) {
        larch.postEvent(event.target, 'keyup', k[0]);
        if (k[1] === 1) {
            event.preventDefault();
            return false;
        }
    }
    return true;
};

larch.__onkeypress = function(event, keys) {
    var k = larch.__handleKeyEvent(event, keys);
    if (k !== undefined) {
        larch.postEvent(event.target, 'keypress', k[0]);
        if (k[1] === 1) {
            event.preventDefault();
            return false;
        }
    }
    return true;
};



larch.__getSegmentIDForEvent = function(src_element) {
    var n = src_element;
    var segment_id = null;
    while (n !== null) {
        if (n.__lch_seg_id) {
            // We have a segment ID
            segment_id = n.__lch_seg_id;
            break;
        }
        n = n.parentNode;
    }

    return segment_id;
};

larch.__buildElementEventMessage = function(segment_id, event_name, event_data) {
    return {
        msgtype: 'event',
        segment_id: segment_id,
        event_name: event_name,
        ev_data: event_data
    };
};



larch.__sendEventMessagesToServer = function(ev_messages) {
    var ev_json = JSON.stringify(ev_messages);

    var ev_data = {
        session_id: larch.__session_id,
        event_data: ev_json
    };

    $.ajax({
        type: 'POST',
        url: '/event',
        data: ev_data,
        success: function(msg) {
            larch.__handleMessagesFromServer(msg);
        },
        dataType: 'json'
    });
};

larch.__postEventMessage = function(ev_msg) {
    var messages = [];

    if (larch.__eventFactoryQueue.length > 0) {
        // Create events from factory queue
        for (var i = 0; i < larch.__eventFactoryQueue.length; i++) {
            var key = larch.__eventFactoryQueue[i];
            var fac = larch.__eventFactoriesBySrcAndName[key];
            var ev_data = fac.event_factory();
            var msg = larch.__buildElementEventMessage(fac.segment_id, fac.event_name, ev_data);
            messages.push(msg);
        }
        // Clear factory queue
        larch.__eventFactoryQueue = [];
        larch.__eventFactoriesBySrcAndName = {};
    }

    // Add the message that we are posting
    messages.push(ev_msg);

    // Send
    larch.__sendEventMessagesToServer(messages);
};


larch.postEvent = function(src_element, event_name, event_data) {
    var segment_id = larch.__getSegmentIDForEvent(src_element);

    if (segment_id !== null) {
        var ev_msg = larch.__buildElementEventMessage(segment_id, event_name, event_data);
        larch.__postEventMessage(ev_msg);
    }
};


larch.postDocumentEvent = function(event_name, event_data) {
    var ev_msg = {
        msgtype: 'event',
        segment_id: null,
        event_name: event_name,
        ev_data: event_data
    };

    larch.__postEventMessage(ev_msg);
};


larch.__eventFactoryQueue = [];
larch.__eventFactoriesBySrcAndName = {};


larch.queueEventFactory = function(src_element, event_name, event_factory) {
    var segment_id = larch.__getSegmentIDForEvent(src_element);
    var key = segment_id + '__' + event_name;

    var fac = {segment_id: segment_id, event_name: event_name, event_factory: event_factory};
    if (!larch.hasQueuedEventFactory(src_element, event_name)) {
        larch.__eventFactoryQueue.push(key);
    }
    larch.__eventFactoriesBySrcAndName[key] = fac;
};

larch.hasQueuedEventFactory = function(src_element, event_name) {
    var segment_id = larch.__getSegmentIDForEvent(src_element);
    var key = segment_id + '__' + event_name;

    return larch.__eventFactoriesBySrcAndName.hasOwnProperty(key);
};


larch.__resourceIdToResource = {};

larch.__createResource = function(rscId, rscUrl) {
    var rsc = {};
    rsc.__rscId = rscId;
    rsc.url = rscUrl;
    rsc.__listeners = [];

    rsc.fetchString = function(handlerFn) {
        $.ajax({
            type: 'GET',
            url: rsc.url,
            //data: ev_data,
            success: handlerFn
            //dataType: 'json'
        });
    };

    rsc.fetchJSON = function(handlerFn) {
        $.ajax({
            type: 'GET',
            url: rsc.url,
            //data: ev_data,
            success: handlerFn,
            dataType: 'json'
        });
    };

    rsc.addListener = function(listener) {
        for (var i = 0; i < rsc.__listeners.length; i++) {
            if (rsc.__listeners[i] === listener) {
                return;
            }
        }

        rsc.__listeners.push(listener);
    };

    rsc.removeListener = function(listener) {
        for (var i = 0; i < rsc.__listeners.length; i++) {
            if (rsc.__listeners[i] === listener) {
                delete rsc.__listeners[i];
                return;
            }
        }
    };

    larch.__resourceIdToResource[rscId] = rsc;
    return rsc;
};

larch.__destroyResource = function(rscId) {
   delete larch.__resourceIdToResource[rscId];
};

larch.__resourceModified = function(rscId) {
    var rsc = larch.__resourceIdToResource[rscId];

    for (var i = 0; i < rsc.__listeners.length; i++) {
        rsc.__listeners[i]();
    }
};




larch.__commands = [];
larch.__userEnteringCommand = false;
larch.__partialCommandKeySequence = null;


larch.registerCommand = function(keySequence, commandId) {
    var cmd = {
        keySequence: keySequence,
        commandId: commandId
    };
    larch.__commands.push(cmd);
};

larch.unregisterCommand = function(commandId) {
    for (var i = 0; i < larch.__commands.length; i++) {
        if (larch.__commands[i].commandId === commandId) {
            delete larch.__commands[i];
            return;
        }
    }
};

larch.__compareKeySequences = function(enteredSequence, commandSequence) {
    if (enteredSequence.length === commandSequence.length) {
        for (var j = 0; j < enteredSequence.length; j++) {
            if (!larch.__matchKeyEvent(enteredSequence[j], commandSequence[j])) {
                console.log("Failed key " + j)
                console.log(enteredSequence[j]);
                console.log(commandSequence[j]);
                return false;
            }
        }
        return true;
    }
    return false;
};

larch.__setupCommandListeners = function() {
    document.body.onkeydown = function(event) {
        if (larch.__userEnteringCommand) {
            // Check for Escape
            event.preventDefault();
            if (event.keyCode == 27) {
                // Quit the command
                larch.__userEnteringCommand = false;
                larch.__partialCommandKeySequence = null;
                console.log("Terminating command");
                return false;
            }
            else {
                console.log("Command: got a key");
                var k = larch.__eventToKey(event);
                var matchingCommand = null;
                larch.__partialCommandKeySequence.push(k);

                for (var i = 0; i < larch.__commands.length; i++) {
                    var cmd = larch.__commands[i];
                    if (larch.__compareKeySequences(larch.__partialCommandKeySequence, cmd.keySequence)) {
                        matchingCommand = cmd;
                        break;
                    }
                }

                if (matchingCommand !== null) {
                    console.log("Command: sending...");
                    larch.postDocumentEvent('command', cmd.commandId);
                    larch.__userEnteringCommand = false;
                    larch.__partialCommandKeySequence = null;
                    return false;
                }
            }
        }
        else {
            // Check for CTRL-M
            if (event.keyCode === 77  &&  event.ctrlKey) {
                event.preventDefault();
                // We have started a command
                larch.__userEnteringCommand = true;
                larch.__partialCommandKeySequence = [];
                console.log("Beginning command");
                return false;
            }
        }

        return true;
    };
};

larch.__onDocumentReady = function(initialisers) {
    larch.__register_segments();
    larch.__executeNodeScripts(initialisers);
    larch.__setupCommandListeners();
};

