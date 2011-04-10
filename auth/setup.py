import os
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'pyramid_mailer',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'WebError',
    'formencode',
    'recaptcha-client',
]
if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')


entry_points = """\
    [paste.app_factory]
    main = auth:main
"""


setup(
    name='auth',
    version='0.0',
    description='auth',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='auth',
    install_requires = requires,
    entry_points = entry_points,
    paster_plugins=['pyramid'],
)
