larch.controls.initCKEditor = function(textArea, config, immediate_events) {
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
