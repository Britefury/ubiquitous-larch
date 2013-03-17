larch.controls.initCodeMirror = function(textArea, config, immediate_events) {
    if (immediate_events) {
        config.onChange = function(editor, edit) {
            var elem = editor.getWrapperElement();
            larch.postEvent(elem, "code_mirror_edit", editor.getValue());
        };
    }
    else {
        config.onChange = function(editor, edit) {
            var elem = editor.getWrapperElement();
            var fac = function() {
                return editor.getValue();
            };
            larch.queueEventFactory(elem, "code_mirror_edit", fac);
        };
    }
    CodeMirror.fromTextArea(textArea, config);
}


