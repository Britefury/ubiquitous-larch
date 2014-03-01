security_warning_page = """
<html>
<head>
<title>Ubiquitous Larch collaborative server</title>
<link rel="stylesheet" type="text/css" href="/static/jquery/css/ui-lightness/jquery-ui-1.10.2.custom.min.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch/larch.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch/larch_login.css"/>
<script type="text/javascript" src="/static/jquery/js/jquery-1.9.1.js"></script>
<script type="text/javascript" src="/static/jquery/js/jquery-ui-1.10.2.custom.min.js"></script>
</head>


<body>
<div class="title_bar">The Ubiquitous Larch</div>


<div class="sec_warning_content">
<h1>Ubiquitous Larch Collaborative Server; Security notice</h1>


<h3>Please read the security warning first, then enable the server</h3>


<p>If you wish to run Ubiquitous Larch on a publicly accessible web server, you need to take security precautions. Running Ubiquitous Larch
will allow other people to run arbitrary Python code on your server. It has been found to be largely impossible to do this in a secure manner.
As a consequence, Ubiquitous Larch uses a global password for security; providing user accounts would give a false sense of security, as one
of your users could use the Python interpreter to access the authentication system to elevate their privileges, making account based
authentication useless. By giving a user the global password, assume that you are granting the user the same access rights available to
the web server. You should assume that allowing access to a Python interpreter would permit:</p>

<ul>
	<li>Access to files stored on the server, including the ability to read, modify and delete</li>
	<li>Installation of mal-ware</li>
	<li>Making arbitrary network connections</li>
	<li>Using CPU and other system resources (an issue on shared servers)</li>
</ul>

<p>Therefore, it would be advisable to ensure that:</p>

<ul>
	<li>No sensitive information is stored on your server</li>
	<li>All data on the server is backed up</li>
	<li>The ability to make external network connections is restricted</li>
	<li>Restricting access to other resources may require that you shut the server down
	when you do not intend to use it</li>
</ul>

<p class="risk">The author(s) of Ubiquitous Larch accept NO responsibility for any damage, or indeed anything that occur as a result of its use.
If you are not comfortable with this, please do not use this software.</p>

<h3>Enabling the collaborative server</h3>

<p>Please edit the file <em>wsgi_ularch.py</em> and modify the line:</p>

<div class="code_block">GLOBAL_PASSWORD = ''</div>

<p>by placing a password between the quotes and restart the server. For example:</p>

<div class="code_block">GLOBAL_PASSWORD = 'abc123'</div>

</div>

<script type="text/javascript">
	$("#submit_button").button();
</script>
</body>
</html>
"""



login_form_page = """
<html>
<head>
<title>Login</title>
<link rel="stylesheet" type="text/css" href="/static/jquery/css/ui-lightness/jquery-ui-1.10.2.custom.min.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch/larch.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch/larch_login.css"/>
<script type="text/javascript" src="/static/jquery/js/jquery-1.9.1.js"></script>
<script type="text/javascript" src="/static/jquery/js/jquery-ui-1.10.2.custom.min.js"></script>
</head>


<body>
<div class="title_bar">The Ubiquitous Larch</div>

<div class="login_form">
<p>Please login:</p>

<form action="/accounts/process_login" method="POST">
<table>
	<tr><td>Password</td><td><input type="password" name="password" class="login_form_text_field"/></td></tr>
	<tr><td></td><td><input id="submit_button" type="submit" value="Login"/></td></tr>
</table>
</form>

{0}

</div>

<script type="text/javascript">
	$("#submit_button").button();
</script>
</body>
</html>
"""