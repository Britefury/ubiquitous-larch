function createStructure() {
	var s = "[";
	var i = 0;
	while (i < 16384)
	{
		s += "<span class=\"prim_int\">" + i + "</span><span class=\"punc\">, </span>";
		i += 1;
	}
	s += "]";
	return s;
}


function insertContent() {
	//var s = createStructure();
	//$("#content").html(s);
	var t1 = (new Date).getTime();
	$("#content").html(global_content);
	var t2 = (new Date).getTime();
	var diff = t2 - t1;
	var deltaTime = "" + diff;
	$("#time").html(deltaTime);
}


function initPage() {
	global_content = createStructure();
}


$(document).ready(initPage);