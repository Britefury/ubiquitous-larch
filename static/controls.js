__larchControls = {};

//
//
// Code Mirror
//
//

__larchControls.codeMirror_onChange = function(editor, edit) {
    var elem = editor.getWrapperElement();
    if (!__larch.hasQueuedEventFactory(elem, "code_mirror_edit")) {
        var fac = function() {
            return editor.getValue();
        };
        __larch.queueEventFactory(elem, "code_mirror_edit", fac);
    }
};

__larchControls.codeMirror_onChangeImmediate = function(editor, edit) {
    var elem = editor.getWrapperElement();
    __larch.postEvent(elem, "code_mirror_edit", editor.getValue());
};

__larchControls.initCodeMirror = function(textArea, config, immediate_events) {
    if (immediate_events) {
        config.onChange = __larchControls.codeMirror_onChangeImmediate;
    }
    else {
        config.onChange = __larchControls.codeMirror_onChange;
    }
    CodeMirror.fromTextArea(textArea, config);
}


//
//
// jQuery slider
//
//

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

__larchControls.init_ckeditor = function(textArea, config, immediate_events) {
    CKEDITOR.inline(textArea, config);
    if (immediate_events) {
        textArea.addEventListener('input', function(){
            __larch.postEvent(textArea, "ckeditor_edit", textArea.innerHTML);
        }, false);
    }
    else {
        textArea.addEventListener('input', function(){
            if (!__larch.hasQueuedEventFactory(textArea, "ckeditor_edit")) {
                var fac = function() {
                    return textArea.innerHTML;
                };
                __larch.queueEventFactory(textArea, "ckeditor_edit", fac);
            }
        }, false);
    }
}

CKEDITOR.disableAutoInline = true;