=========================
HTTP plugins for buildout
=========================

HTTP Basic-Authenication
========================

Whith this extension it is possible to define password protected
package directories without specifying the password and user in the
url.

Example: protected location http://www.example.com/dist


File buildout.cfg:
[buildout]
find-links=http://www.example.com/dist
extensions=lovely.buildouthttp

Create the password file, this file contains all authentication
information. Each row consists of realm, uri, username, password.

file ~/.buildout/.httpauth:
Example com realm, http://www.example.com, username, secret


Credits
=======

Thanks to Tarek Ziade for bugfixes and extensions.
