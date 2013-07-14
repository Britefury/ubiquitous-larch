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
        larch.postEvent(textArea, "ckeditor_focus", null);
    });
    c.on("blur", function() {
        larch.postEvent(textArea, "ckeditor_blur", null);
    });
};

CKEDITOR.disableAutoInline = true;
