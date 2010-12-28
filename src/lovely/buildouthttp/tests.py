import doctest
import unittest
from zope.testing.doctest import DocFileSuite, DocTestSuite
import tempfile
import shutil


def setUp(test):
    test.globs['tmp'] = tempfile.mkdtemp()


def tearDown(test):
    shutil.rmtree(test.globs['tmp'])


def test_suite():
    uSuites = (
        DocFileSuite(
            'install.txt',
            setUp=setUp,
            tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        DocTestSuite(
            'lovely.buildouthttp.buildouthttp',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        )
    return unittest.TestSuite(uSuites)
