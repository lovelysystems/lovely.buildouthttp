import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.rst')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

name='lovely.buildouthttp'
setup(
    name = name,
    version = "0.6.0",
    author = "Lovely Systems GmbH",
    author_email = "office@lovelysystems.com",
    description = "Buildout extension to add http authentication "
                  "for find-links and download recipies",
    long_description = long_description,
    license = "ZPL 2.1",
    keywords = "buildout http authentication github",
    url='http://github.com/lovelysystems/lovely.buildouthttp',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    install_requires = ['setuptools', 'zc.buildout', 'six'],
    extras_require = dict(
        test = ['zope.testing']
        ),
    entry_points = {'zc.buildout.extension':
                    ['default = %s.buildouthttp:install' % name]
                    },
    zip_safe = False,
    classifiers = [
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    )
