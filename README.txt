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

Note that basic auth also works with any recipe using
zc.buildout.download (e.g. hexagonit.recipe.download) because this
extension also overwrites the url opener of zc.buildout.

Github Private Downloads
========================

Private downloads on http://github.com/ require authorization to download.
The previous token-based authentication system based on the v2 API (see
http://github.com/blog/170-token-authentication) is no longer supported by
GitHub as of June 1 2012; You must now request a v3 API token and use that
instead.

Requesting a new API token can be done in one line using ``curl`` (please
substitute your own github username and password):

    curl -s -X POST -d '{"scopes": ["repo"], "note": "my API token"}' \
        https://${user}:${pass}@api.github.com/authorizations | grep token

Now set the value of github.token to the hash returned from the command above:

    git config --global github.accesstoken ${token}

Note that the v3 API does not require your github username to work, and can
be removed from your configuration if you wish.

For details on managing authorization GitHub's OAuth tokens, see the API
documentation: http://developer.github.com/v3/oauth/#oauth-authorizations-api

URL to download a tag or branch::

    https://api.github.com/repos/<gituser>/<repos>/tarball/master

URL to downlad a "download"::

    https://github.com/downloads/<gituser>/<repos>/<name>

As some eggs on PyPi also use public Github download URLs you may want to
whitelist the repos that authentication is required for as Github will
return a 401 error code even for public repositories if the wrong auth
details are provided.
To do this just list each repo in the format `<gituser>/<repos>` one per
line in the buildout config `github-repos`::

    [buildout]
    extensions = lovely.buildouthttp
    github-repos = lovelysystems/lovely.buildouthttp
                   bitly/asyncmongo


Credits
=======

Thanks to Tarek Ziade, Kevin Williams and Wesley Mason for bugfixes and extensions.
