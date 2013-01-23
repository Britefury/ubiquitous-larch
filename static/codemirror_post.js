__pythonCodeArea = {};

__pythonCodeArea.onChange = function(editor, edit) {
    var elem = editor.getWrapperElement();
    __larch.postEvent(elem, "changed", editor.getValue());
};

__pythonCodeArea.initPythonCodeArea = function(textArea) {
    var config = {
        mode: {name: "python",
            version: 2,
            singleLineStringErrors: false},
        lineNumbers: true,
        indentUnit: 4,
        tabMode: "shift",
        matchBrackets: true,
        onChange: __pythonCodeArea.onChange
    };
    CodeMirror.fromTextArea(textArea, config);
};


__pythonCodeArea.initPythonCodeAreaNonEditable = function(textArea) {
    var config = {
        mode: {name: "python",
            version: 2,
            singleLineStringErrors: false},
        lineNumbers: true,
        indentUnit: 4,
        tabMode: "shift",
        matchBrackets: true,
        editable: false
    };
    CodeMirror.fromTextArea(textArea, config);
};
