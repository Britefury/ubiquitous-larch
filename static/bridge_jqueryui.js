//
//
// jQuery UI controls
//
//

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


