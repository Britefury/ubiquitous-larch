__larchControls = {};

__larchControls.codeMirror_onChange = function(editor, edit) {
    var elem = editor.getWrapperElement();
    __larch.postEvent(elem, "code_mirror_edit", editor.getValue());
};

__larchControls.initCodeMirror = function(textArea, config) {
    config.onChange = __larchControls.codeMirror_onChange;
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

__larchControls.initMenu = function(node) {
    $(node).menu( {
        select: function(event, ui) {
            var node = ui.item.get(0);
            __larch.postEvent(node, "menu_select", null);
        }
    });
}

__larchControls.init_ckeditor = function(textArea, config) {
    CKEDITOR.inline(textArea, config);
    textArea.addEventListener('input', function(){
        __larch.postEvent(textArea, "ckeditor_edit", textArea.innerHTML);
    }, false);
}

CKEDITOR.disableAutoInline = true;