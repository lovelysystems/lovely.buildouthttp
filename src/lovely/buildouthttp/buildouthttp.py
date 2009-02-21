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

def install(buildout=None):
    try:
        pwdsf = file(os.path.join(os.path.expanduser('~'),
                                  '.buildout',
                                  '.httpauth'))
    except IOError, e:
        log.warn('Could not load authentication information: %s' % e)
        return
    reader = csv.reader(pwdsf)
    auth_handler = CredHandler()
    for row in reader:
        if len(row) != 4:
            continue
        realm, uris, user, password = (el.strip() for el in row)
        log.debug('Added credentials %r, %r' % (realm, uris))
        auth_handler.add_password(realm, uris, user, password)
        handlers = []
        if urllib2._opener is not None:
            handlers[:] = urllib2._opener.handlers
        handlers.insert(0, auth_handler)
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)
