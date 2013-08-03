//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************

larch.controls.initCKEditor = function(textArea, config, immediate_events) {
    var c = CKEDITOR.inline(textArea, config);
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
    c.on("focus", function() {
        larch.controls.grabFocus(textArea);
        larch.postEvent(textArea, "ckeditor_focus", null);
    });
    c.on("blur", function() {
        larch.postEvent(textArea, "ckeditor_blur", null);
    });

    CKEDITOR.disableAutoInline = true;
};





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
        larch.controls.grabFocus(elem);
        larch.postEvent(elem, "code_mirror_focus", null);
    });
    c.on("blur", function(editor) {
        var elem = editor.getWrapperElement();
        larch.postEvent(elem, "code_mirror_blur", null);
    });
};




//
//
// jQuery UI controls
//
//

larch.controls.initButton = function(node, options) {
    $(node).button(options);
};

larch.controls.initSlider = function(node, respondToSlide, options) {
    options.change = function(event, ui) {
        larch.postEvent(node, "slider_change", ui.value)
    };
    if (respondToSlide) {
        options.slide = function(event, ui) {
            larch.postEvent(node, "slider_slide", ui.value)
        };
    }
    $(node).slider(options);
};

larch.controls.initRangeSlider = function(node, respondToSlide, options) {
    options.change = function(event, ui) {
        larch.postEvent(node, "slider_change", ui.values)
    };
    if (respondToSlide) {
        options.slide = function(event, ui) {
            larch.postEvent(node, "slider_slide", ui.values)
        };
    }
    $(node).slider(options);
};

larch.controls.initSpinner = function(node) {
    $(node).spinner({
        change: function(event, ui) {
            larch.postEvent(node, "spinner_change", ui.value)
        }
    });
};

larch.controls.initMenu = function(node, options) {
    options.select = function(event, ui) {
        var node = ui.item.get(0);
        larch.postEvent(node, "menu_select", null);
    };
    $(node).menu(options);
};

larch.controls.initDialog = function(node, options) {
    $(node).dialog(options);
};

larch.controls.initTextEntry = function(node) {
    node.oninput = function() {
        larch.postEvent(node, "text_entry_edit", node.value);
    };
};

larch.controls.initSelect = function(node) {
    node.onchange = function() {
        larch.postEvent(node, "select_choose", node.value);
    };
};



larch.controls.__focus = null;

larch.controls.makeFocusable = function(node) {
    var q = $(node);
    q.addClass("larch_ui_focusable");
    q.click(function() {
        larch.controls.grabFocus(node);
    });
};

larch.controls.grabFocus = function(node) {
    var focusable = $(node).closest(".larch_ui_focusable");

    if (focusable.length === 1) {
        if (larch.controls.__focus !== null) {
            $( larch.controls.__focus).removeClass("larch_ui_focused");
            larch.postEvent(larch.controls.__focus, "lose_focus", null);
        }

        larch.controls.__focus = focusable.get(0);
        focusable.addClass("larch_ui_focused");
        larch.postEvent(larch.controls.__focus, "gain_focus", null);
    }
};
