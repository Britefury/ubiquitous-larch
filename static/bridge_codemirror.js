//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************

larch.controls.initCodeMirror = function(textArea, config, immediate_events) {
    var c = CodeMirror.fromTextArea(textArea, config);
    if (immediate_events) {
        c.on("change", function(editor, edit) {
            var elem = editor.getWrapperElement();
            larch.postEvent(elem, "code_mirror_edit", editor.getValue());
        });
    }
    else {
        c.on("change", function(editor, edit) {
            var elem = editor.getWrapperElement();
            var fac = function() {
                return editor.getValue();
            };
            larch.queueEventFactory(elem, "code_mirror_edit", fac);
        });
    }
    c.on("focus",  function(editor) {
        var elem = editor.getWrapperElement();
        larch.postEvent(elem, "code_mirror_focus", null);
    });
    c.on("blur", function(editor) {
        var elem = editor.getWrapperElement();
        larch.postEvent(elem, "code_mirror_blur", null);
    });
};


