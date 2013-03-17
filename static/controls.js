larchControls = {};

//
//
// Code Mirror
//
//

larchControls.initCodeMirror = function(textArea, config, immediate_events) {
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


//
//
// jQuery slider
//
//

larchControls.initSlider = function(node) {
    var q = $(node);
    $(node).slider({
        change: function(event, ui) {
            larch.postEvent(node, "slider_change", ui.value)
        }
    });
}

larchControls.initMenu = function(node) {
    $(node).menu( {
        select: function(event, ui) {
            var node = ui.item.get(0);
            larch.postEvent(node, "menu_select", null);
        }
    });
}

larchControls.initCKEditor = function(textArea, config, immediate_events) {
    CKEDITOR.inline(textArea, config);
    if (immediate_events) {
        textArea.addEventListener('input', function(){
            larch.postEvent(textArea, "ckeditor_edit", textArea.innerHTML);
        }, false);
    }
    else {
        textArea.addEventListener('input', function(){
            var fac = function() {
                return textArea.innerHTML;
            };
            larch.queueEventFactory(textArea, "ckeditor_edit", fac);
        }, false);
    }
}

CKEDITOR.disableAutoInline = true;