##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""

import urllib2
import os
import sys
import csv
import logging
import subprocess
import urllib
from zc.buildout import download
import urlparse

log = logging.getLogger('lovely.buildouthttp')

def get_github_credentials():

    """returns the credentials for the local git installation by using
    git config"""

    p = subprocess.Popen("git config github.token",
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    rc = p.wait()
    if rc:
        # failure to get config, so return silently
        return None
    token = p.stdout.readline().strip()
    pipe = subprocess.Popen("git config github.user",
                            shell=True,
                            stdout=subprocess.PIPE).stdout
    login = pipe.readline().strip()
    pipe.close()
    if login and token:
        log.debug("Found github credentials for user %r", login)
        return login, token


class GithubHandler(urllib2.BaseHandler):

    """This handler creates a post request with login and token, see
    http://github.com/blog/170-token-authentication for details"""

    def __init__(self, login, token):
        self._login = login
        self._token = token

    def https_request(self, req):
        if req.get_method() == 'GET' and req.get_host() == 'github.com':
            log.debug("Found private github url %r", req.get_full_url())
            data = urllib.urlencode(dict(login=self._login,
                                         token=self._token))
            timeout = getattr(req, 'timeout', 60)
            if hasattr(req, 'timeout'):
                timeout = req.timeout
            req = urllib2.Request(req.get_full_url(), data)
            req.timeout = timeout
        return req

class CredHandler(urllib2.HTTPBasicAuthHandler):

    """This handler adds basic auth credentials to the request upon a 401

    >>> auth_handler = CredHandler()
    >>> auth_handler.add_password('myrealm', 'http://example.com',
    ...                           'user', 'password')

    >>> from StringIO import StringIO
    >>> fp = StringIO('The error body')
    >>> req = urllib2.Request('http://example.com')
    >>> auth_handler.http_error_401(req, fp, 401, 'msg', {})
    """

    def http_error_401(self, req, fp, code, msg, headers):
        log.debug('getting url: %r' % req.get_full_url())
        try:
            res =  urllib2.HTTPBasicAuthHandler.http_error_401(
                self,req, fp, code, msg, headers)
        except urllib2.HTTPError, err:
            log.error('failed to get url: %r %r', req.get_full_url(), err.code)
            raise
        except Exception, err:
            log.error('failed to get url: %r %s', req.get_full_url(), str(err))
            raise
        else:
            if res is None:
                log.error('failed to get url: %r, check your realm',
                          req.get_full_url())
            elif res.code>=400:
                log.error('failed to get url: %r %r', res.url, res.code)
            else:
                log.debug('got url: %r %r', res.url, res.code)
            return res

def install(buildout=None, pwd_path=None):
    """
    By default the install function looks for the password file at
    ~/.buildout/.httpauth and installs a basic auth opener.

    It does not fail if the file cannot be found.
    >>> install()

    We can supply the path to the file for testing.

    >>> install(pwd_path='a')

    If the file cannot be parsed an exception is raised.

    >>> fp = os.path.join(tmp,'pwd.txt')
    >>> import os
    >>> f = file(fp, 'w')
    >>> f.write('The realm,https://example.com/ something')
    >>> f.close()
    >>> install(pwd_path=fp)
    Traceback (most recent call last):
    ...
    RuntimeError: Authentication file cannot be parsed ...pwd.txt:1

    >>> f = file(fp, 'w')
    >>> f.write('The realm,https://example.com/,username,password')
    >>> f.close()
    >>> install(pwd_path=fp)
    """

    try:
        pwd_path = pwd_path or os.path.join(os.path.expanduser('~'),
                                  '.buildout',
                                  '.httpauth')
        pwdsf = file(pwd_path)
    except IOError, e:
        log.warn('Could not load authentication information: %s' % e)
        return


    try:
        reader = csv.reader(pwdsf)
        auth_handler = CredHandler()
        github_creds = get_github_credentials()
        new_handlers = []
        if github_creds:
            new_handlers.append(GithubHandler(*github_creds))

        creds = []
        for l, row in enumerate(reader):
            if len(row) != 4:
                raise RuntimeError(
                    "Authentication file cannot be parsed %s:%s" % (
                        pwd_path, l+1))
            realm, uris, user, password = (el.strip() for el in row)
            creds.append((realm, uris, user, password))
            log.debug('Added credentials %r, %r' % (realm, uris))
            auth_handler.add_password(realm, uris, user, password)
        if creds:
            new_handlers.append(auth_handler)
            download.url_opener = URLOpener(creds)
        if new_handlers:
            if urllib2._opener is not None:
                handlers = urllib2._opener.handlers[:]
                handlers[:0] = new_handlers
            else:
                handlers = new_handlers
            opener = urllib2.build_opener(*handlers)
            urllib2.install_opener(opener)
    finally:
        pwdsf.close()

class URLOpener(download.URLOpener):

    def __init__(self, creds):
        self.creds = {}
        for realm, uris, user, password in creds:
            parts = urlparse.urlparse(uris)
            self.creds[(parts[1], realm)] = (user, password)
        download.URLOpener.__init__(self)

    def prompt_user_passwd(self, host, realm):
        creds = self.creds.get((host, realm))
        if creds:
            return creds
        return download.URLOpener.prompt_user_passwd(self, host, realm)
