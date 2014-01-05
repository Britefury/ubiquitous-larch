To start 'The Ubiquitous Larch', from the command line:

> python start_ularch.py

Then point your browser to:

http://127.0.0.1:5000/






Starting a collaborative Ubiquitous Larch server
===========

PLEASE READ THE SECURITY WARNING BELOW

The author(s) of Ubiquitous Larch accept NO responsibility for any damage, or indeed anything that occur as a result of its use.
If you are not comfortable with this, please do not use this software.

To start Ubiquitous Larch in collaborative mode, allowing others to view and edit your documents, use the WSGI app, available from the wsgi_ularch module.
Note that you may need to change the 'DOCUMENTS_PATH' and 'DOCUMENTATION_PATH' settings at the top of the wsgi_ularch module to point to the appropriate
paths.

WARNING! Running Ubiquitous Larch will allow other people to run arbitrary Python code on your server. It has been found to be largely impossible to do this in a secure manner.
As a consequence, Ubiquitous Larch does not provide any accounts or password protection that could give a false sense of security, as they
could be too easily bypassed by an attacker. Allowing access to a Python console would permit:

- Access to files stored on the server, including the ability to read, modify and delete
- Installation of mal-ware
- Making arbitrary network connections
- Using CPU and other system resources (an issue on shared servers)

Therefore, it would be advisable to ensure that:

- No sensitive information is stored on your server
- All data on the server is backed up
- The ability to make external network connections is restricted
- Restricting access to other resources may require that you shut the server down when you do not intend to use it


