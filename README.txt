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

Github Private Downloads
========================

Private downloads on http://github.com/ are protected by a user token
(see: http://github.com/blog/170-token-authentication). This extension
allows to use such urls too. It uses the global git configuration for
``github.user`` and ``github.token``. For setting up this config see
http://github.com/blog/180-local-github-config.

Credits
=======

Thanks to Tarek Ziade for bugfixes and extensions.
