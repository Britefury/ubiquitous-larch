//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************

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

