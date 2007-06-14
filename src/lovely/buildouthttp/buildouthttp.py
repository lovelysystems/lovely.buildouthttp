##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import urllib2
import os
import sys
import csv
import logging
log = logging.getLogger('lovely.buildouthttp')

def install(buildout=None):
    try:
        pwdsf = file(os.path.join(os.path.expanduser('~'),
                                  '.buildout',
                                  '.httpauth'))
    except IOError, e:
        log.warn('Could not load authentication information: %s' % e)
        return
    reader = csv.reader(pwdsf)
    auth_handler = urllib2.HTTPBasicAuthHandler()
    for row in reader:
        realm, uris, user, password = row
        auth_handler.add_password(realm, uris, user, password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
