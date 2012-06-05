function handleCommandFromServer(command) {
    var cmd_type = command.cmd_type;
    if (cmd_type == "replace_fragment") {
        var frag_id = command.frag_id;
        var frag_content = command.frag_content;
        $("#"+frag_id).html(frag_content);
    }
    else {
        // Unreckognised command
        alert("Unreckognised command" + cmd);
    }
}

function handleCommandsFromServer(commands) {
    for (var i = 0; i < commands.length; i++) {
        handleCommandFromServer(commands[i]);
    }
}

function handleEventResponse(msgJson) {
    var response = eval(msgJson);
    handleCommandsFromServer(response);
}


function postEvent(ev) {
    $.ajax("event").done(function(msg) {handleEventResponse(msg)});
}


