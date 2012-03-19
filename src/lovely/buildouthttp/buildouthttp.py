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
$Id: buildouthttp.py 116763 2010-09-23 12:16:01Z adamg $
"""

import urllib2
import os
import sys
import csv
import logging
import subprocess
import urllib
from StringIO import StringIO
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
            full_url = '%s?%s' % (req.get_full_url(), data)
            req = urllib2.Request(full_url)
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
        try:
            #python 2.6 introduces this attribute and fails the request on 5
            #but since we're process global this fails on the 5th download
            #there's no reset_retry_count(), so clear it here:
            self.retried = 0
        except AttributeError:
            pass

        log.debug('getting url: %r' % req.get_full_url())
        try:
            res = urllib2.HTTPBasicAuthHandler.http_error_401(
                self, req, fp, code, msg, headers)
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
            elif res.code >= 400:
                log.error('failed to get url: %r %r', res.url, res.code)
            else:
                log.debug('got url: %r %r', res.url, res.code)
            return res


def install(buildout=None, pwd_path=None):
    pwdsf = StringIO()
    combined_creds = []
    github_creds = None
    creds = []
    local_pwd_path = ''
    if buildout is not None:
        local_pwd_path = os.path.join(
            buildout['buildout']['directory'],
            '.httpauth')
    system_pwd_path = os.path.join(
        os.path.expanduser('~'),
        '.buildout',
        '.httpauth')

    def combine_cred_file(file_path, combined_creds):
        if file_path is None or not os.path.exists(file_path):
            return
        cred_file = file(file_path)
        combined_creds += [l.strip() for l in cred_file.readlines() if l.strip()]
        cred_file.close()
    # combine all the possible .httpauth files together
    combine_cred_file(pwd_path, combined_creds)
    combine_cred_file(local_pwd_path, combined_creds)
    combine_cred_file(system_pwd_path, combined_creds)
    pwdsf.write("\n".join(combined_creds))
    pwdsf.seek(0)
    if not pwdsf.len:
        pwdsf = None
        log.warn('Could not load authentication information')
    try:
        auth_handler = CredHandler()
        github_creds = get_github_credentials()
        new_handlers = []
        if github_creds:
            new_handlers.append(GithubHandler(*github_creds))
        if pwdsf:
            for l, row in enumerate(csv.reader(pwdsf)):
                if len(row) != 4:
                    raise RuntimeError(
                        "Authentication file cannot be parsed %s:%s" % (
                            pwd_path, l + 1))
                realm, uris, user, password = (el.strip() for el in row)
                creds.append((realm, uris, user, password))
                log.debug('Added credentials %r, %r' % (realm, uris))
                auth_handler.add_password(realm, uris, user, password)
        if creds:
            new_handlers.append(auth_handler)
        if creds or github_creds:
            download.url_opener = URLOpener(creds, github_creds)
        if new_handlers:
            if urllib2._opener is not None:
                handlers = urllib2._opener.handlers[:]
                handlers[:0] = new_handlers
            else:
                handlers = new_handlers
            opener = urllib2.build_opener(*handlers)
            urllib2.install_opener(opener)
    finally:
        if pwdsf:
            pwdsf.close()


class URLOpener(download.URLOpener):

    def __init__(self, creds, github_creds):
        self.creds = {}
        self.github_creds = github_creds
        for realm, uris, user, password in creds:
            parts = urlparse.urlparse(uris)
            self.creds[(parts[1], realm)] = (user, password)
        download.URLOpener.__init__(self)

    def retrieve(self, url, filename=None, reporthook=None, data=None):
        if self.github_creds and not data:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(
                url)
            if scheme == 'https' and netloc == 'github.com':
                log.debug("Appending github credentials to url %r", url)
                login, token = self.github_creds
                data = urllib.urlencode(dict(login=login,
                                             token=token))
                query += '&%s' % data
            url = urlparse.urlunparse((scheme, netloc, path, params,
                                       query, fragment))
        return download.URLOpener.retrieve(self, url, filename,
                                           reporthook, data)

    def prompt_user_passwd(self, host, realm):
        creds = self.creds.get((host, realm))
        if creds:
            return creds
        return download.URLOpener.prompt_user_passwd(self, host, realm)
