//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************

larch.controls.initMathquill = function(span, editable, immediate_events) {
    var math;
    if (editable) {
        math = $(span).mathquill('editable');
        if (immediate_events) {
            math.bind('keydown keypress', function() {
                setTimeout(function() {
                    var latexSource = math.mathquill('latex');
                    larch.postEvent(span, "mathquill_edit", latexSource);
                });
            });
        }
        else {
            math.bind('keydown keypress', function() {
                setTimeout(function() {
                    var fac = function() {
                        return math.mathquill('latex');
                    };
                    larch.queueEventFactory(span, "mathquill_edit", fac);
                });
            });
        }
    }
    else {
        $(span).mathquill();
    }
};

