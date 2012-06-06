$(document).ready(function(){
    var onChange = function(editor, edit) {
        var elem = editor.getWrapperElement();
        elem = $(elem);
        __larch.postEvent(elem, "changed", editor.getValue());
    };

    var codeAreas = $('.python_code');
    var config = {
        mode: {name: "python",
            version: 2,
            singleLineStringErrors: false},
        lineNumbers: true,
        indentUnit: 4,
        tabMode: "shift",
        matchBrackets: true,
        onChange: onChange
    };
    for (var i = 0; i < codeAreas.size(); i++) {
        CodeMirror.fromTextArea(codeAreas.get(i), config);
    }
});