=========================
HTTP plugins for buildout
=========================

HTTP Basic-Authentication
=========================

With this extension it is possible to define password protected
package directories without specifying the password and user in the
url.

Let's take the example protected location, ``http://www.example.com/dist``

First we would need to add the extension and the find link for our
protected location::

    [buildout]
    find-links = http://www.example.com/dist
    extensions = lovely.buildouthttp

Then create the ``.httpauth`` password file, this file contains all
authentication information. The ``.httpauth`` file can be placed in the root of
the current buildout or in the ``~/.buildout`` directory. Each row consists of
``realm, uri, username, password``.

Here is an example of the ``.httpauth`` file::

    Example com realm, http://www.example.com, username, secret

For instances where you do not wish to provide a plaintext .httpauth file,
a [lovely.buildouthttp] stanza can be added of the following form::

    [lovely.buildouthttp]
    realm = myrealm
    uri = http://example.com
    user = username
    password = password # storing passwords in plaintext is not recommended
    prompt = yes

Any *or none* of the "realm", "uri", "user", and "password" keys can be used.
The "prompt" key then determines whether buildout pauses to ask the user for
any missing authentication information.

Note that basic auth also works with any recipe using
zc.buildout.download (e.g. hexagonit.recipe.download) because this
extension also overwrites the url opener of zc.buildout.

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
