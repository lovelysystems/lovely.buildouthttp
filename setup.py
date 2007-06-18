from setuptools import setup, find_packages

name='lovely.buildouthttp'
setup(
    name=name,
    version = "0.1.0a2",
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "Specialized zc.buildout plugin to add http basic" \
                  "authentication support with a pwd file.",
    license = "ZPL 2.1",
    keywords = "buildout http authentication",
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    install_requires = ['setuptools'],
    zip_safe=False,
    entry_points = {'zc.buildout.extension':
                    ['default = %s.buildouthttp:install' % name]
                    },
    )
