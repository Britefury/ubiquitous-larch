__larchControls = {};

__larchControls.onChange = function(editor, edit) {
    var elem = editor.getWrapperElement();
    __larch.postEvent(elem, "code_mirror_edit", editor.getValue());
};

__larchControls.initCodeMirror = function(textArea, config) {
    config.onChange = __larchControls.onChange;
    CodeMirror.fromTextArea(textArea, config);
}

__larchControls.initSlider = function(node) {
    var q = $(node);
    $(node).slider({
        change: function(event, ui) {
            __larch.postEvent(node, "slider_change", ui.value)
        }
    });
}