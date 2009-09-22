##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
log = logging.getLogger('lovely.buildouthttp')

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
            res =  urllib2.HTTPBasicAuthHandler.http_error_401(self,req, fp, code,
                                                           msg,
                                                           headers)
        except urllib2.HTTPError, err:
            log.error('failed to get url: %r %r' % (req.get_full_url(), err.code))
            raise
        except Exception, err:
            log.error('failed to get url: %r %s' % (req.get_full_url(), str(err)))
            raise
        else:
            if res is None:
                log.error('failed to get url: %r, check your realm' % req.get_full_url())
            elif res.code>=400:
                log.error('failed to get url: %r %r' % (res.url, res.code))
            else:
                log.debug('got url: %r %r' % (res.url, res.code))
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
    reader = csv.reader(pwdsf)
    auth_handler = CredHandler()
    for l, row in enumerate(reader):
        if len(row) != 4:
            raise RuntimeError(
                "Authentication file cannot be parsed %s:%s" % (
                    pwd_path, l+1))
        realm, uris, user, password = (el.strip() for el in row)
        log.debug('Added credentials %r, %r' % (realm, uris))
        auth_handler.add_password(realm, uris, user, password)
        handlers = []
        if urllib2._opener is not None:
            handlers[:] = urllib2._opener.handlers
        handlers.insert(0, auth_handler)
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)
