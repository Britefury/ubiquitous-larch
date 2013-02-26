__codeMirrorBridge = {};

__codeMirrorBridge.onChange = function(editor, edit) {
    var elem = editor.getWrapperElement();
    __larch.postEvent(elem, "code_mirror_edit", editor.getValue());
};

__codeMirrorBridge.initCodeMirror = function(textArea, config) {
    config.onChange = __codeMirrorBridge.onChange;
    CodeMirror.fromTextArea(textArea, config);
}

