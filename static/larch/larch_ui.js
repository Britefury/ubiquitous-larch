//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************

larch.controls.initCKEditor = function(textArea, config, immediate_events, channel) {
    var ignoreChanges = [false];

    var c = CKEDITOR.inline(textArea, config);
    if (immediate_events) {
        textArea.addEventListener('input', function(){
            if (!ignoreChanges[0]) {
                larch.postEvent(textArea, "ckeditor_edit", textArea.innerHTML);
            }
        }, false);
    }
    else {
        textArea.addEventListener('input', function(){
            if (!ignoreChanges[0]) {
                var fac = function() {
                    return textArea.innerHTML;
                };
                larch.queueEventFactory(textArea, "ckeditor_edit", fac);
            }
        }, false);
    }
    c.on("focus", function() {
        larch.controls.grabFocus(textArea);
        larch.postEvent(textArea, "ckeditor_focus", null);
    });
    c.on("blur", function() {
        larch.postEvent(textArea, "ckeditor_blur", null);
    });

    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            c.setData(message);
            ignoreChanges[0] = false;
        });
    }

    CKEDITOR.disableAutoInline = true;
};





larch.controls.initCodeMirror = function(textArea, config, immediate_events, channel) {
    var ignoreChanges = [false];

    var c = CodeMirror.fromTextArea(textArea, config);
    if (immediate_events) {
        c.on("change", function(editor, edit) {
            if (!ignoreChanges[0]) {
                var elem = editor.getWrapperElement();
                larch.postEvent(elem, "code_mirror_edit", editor.getValue());
            }
        });
    }
    else {
        c.on("change", function(editor, edit) {
            if (!ignoreChanges[0]) {
                var elem = editor.getWrapperElement();
                var fac = function() {
                    return editor.getValue();
                };
                larch.queueEventFactory(elem, "code_mirror_edit", fac);
            }
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

    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            c.getDoc().setValue(message);
            ignoreChanges[0] = false;
        });
    }
};




//
//
// jQuery UI controls
//
//

larch.controls.initButton = function(node, options) {
    $(node).button(options);
};

larch.controls.initSlider = function(node, respondToSlide, options, channel) {
    var ignoreChanges = [false];
    options.change = function(event, ui) {
        if (!ignoreChanges[0]) {
            larch.postEvent(node, "slider_change", ui.value)
        }
    };
    if (respondToSlide) {
        options.slide = function(event, ui) {
            if (!ignoreChanges[0]) {
                larch.postEvent(node, "slider_slide", ui.value)
            }
        };
    }
    var control = $(node).slider(options);
    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            control.slider('value', message);
            ignoreChanges[0] = false;
        });
    }
};

larch.controls.initRangeSlider = function(node, respondToSlide, options, channel) {
    var ignoreChanges = [false];
    options.change = function(event, ui) {
        if (!ignoreChanges[0]) {
            larch.postEvent(node, "slider_change", ui.values)
        }
    };
    if (respondToSlide) {
        options.slide = function(event, ui) {
            if (!ignoreChanges[0]) {
                larch.postEvent(node, "slider_slide", ui.values)
            }
        };
    }
    var control = $(node).slider(options);
    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            control.slider('values', message);
            ignoreChanges[0] = false;
        });
    }
};

larch.controls.initSpinner = function(node, channel) {
    var ignoreChanges = [false];
    var control = $(node).spinner({
        spin: function(event, ui) {
            if (!ignoreChanges[0]) {
                larch.postEvent(control.get(0), "spinner_change", ui.value);
            }
        }
    });

    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            control.spinner('value', message);
            ignoreChanges[0] = false;
        });
    }
};

larch.controls.initTextEntry = function(node, immediateEvents, channel) {
    var ignoreChanges = [false];

    if (immediateEvents) {
        node.oninput = function() {
            if (!ignoreChanges[0]) {
                larch.postEvent(node, "text_entry_edit", node.value);
            }
        };
    }
    else {
        node.oninput = function() {
            if (!ignoreChanges[0]) {
                larch.queueEventFactory(node, "text_entry_edit", function() {
                    return node.value;
                });
            }
        };
    }

    if (channel !== undefined) {
        channel.addListener(function(message) {
            ignoreChanges[0] = true;
            node.value = message;
            ignoreChanges[0] = false;
        });
    }
};

larch.controls.initSelect = function(node) {
    node.onchange = function() {
        larch.postEvent(node, "select_choose", node.value);
    };
};


larch.controls.initMenu = function(node, options) {
    options.select = function(event, ui) {
        var node = ui.item.get(0);
        larch.postEvent(node, "menu_select", null);
    };
    $(node).menu(options);
};



//
// FOCUS
//

larch.controls.__focus = null;

larch.controls.initFocusable = function(node) {
    var q = $(node);
    q.addClass("larch_ui_focusable");
    q.click(function() {
        larch.controls.grabFocus(node);
    });
};

larch.controls.shutdownFocusable = function(node) {
    var q = $(node);
    q.addClass("larch_ui_focusable");
    q.click(function() {
        larch.controls.ungrabFocus(node);
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

larch.controls.ungrabFocus = function(node) {
    var focusable = $(node).closest(".larch_ui_focusable");

    if (focusable.length === 1) {
        if (focusable.hasClass("larch_ui_focused")) {
            focusable.removeClass("larch_ui_focused");
            larch.postEvent(focusable.get(0), "lose_focus", null);
        }
    }
};




larch.controls.initToggleCommandBarButton = function(node) {
    return $(node).click(function() {
        if (larch.__commandBar === null) {
            larch.__showCommandBar();
        }
        else {
            larch.__commandBar.close();
        }
    }).button({icons: {primary: 'ui-icon-bullet'}});
};



larch.controls.initForm = function(node) {
    var form = $(node);
    form.submit(function() {
        var segment_id = larch.__getSegmentIDForEvent(node);
        form.ajaxSubmit({
            data: {__larch_segment_id: segment_id},
            url: '/form/' + larch.__view_id,
            dataType: 'json',
            type: 'POST',
            success: function(msg) {
                larch.__handleMessagesFromServer(msg);
            }
        });
        return false;
    });
    form.ajaxForm();
};




larch.controls.createNotyPopup = function(popup_id, nodes, options) {
    options.text = $(nodes);
    options.callback = {};
    options.callback.afterClose = function() {
        larch.__notifyPopupClosed(popup_id);
    };
    noty(options);
};


larch.controls.createDialog = function(popup_id, nodes, options) {
    options.close = function(event, ui) {
        larch.__notifyPopupClosed(popup_id);
    };
    var contents = null;
    if (nodes.length != 1) {
        contents = $('<div></div>');
        contents.append(nodes);
    }
    else {
        contents = nodes[0];
    }
    $(contents).dialog(options);
};


