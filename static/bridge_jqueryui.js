//
//
// jQuery UI controls
//
//

larch.controls.initButton = function(node) {
    $(node).button();
}

larch.controls.initSlider = function(node) {
    var q = $(node);
    $(node).slider({
        change: function(event, ui) {
            larch.postEvent(node, "slider_change", ui.value)
        }
    });
}

larch.controls.initMenu = function(node, options) {
    options.select = function(event, ui) {
        var node = ui.item.get(0);
        larch.postEvent(node, "menu_select", null);
    };
    $(node).menu(options);
}

larch.controls.initDialog = function(node, options) {
    $(node).dialog(options);
}

larch.controls.initTextEntry = function(node) {
    node.oninput = function() {
        larch.postEvent(node, "text_entry_edit", node.value);
    };
}
