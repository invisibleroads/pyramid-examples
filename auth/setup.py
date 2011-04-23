import os
import sys

from setuptools import setup, find_packages


requires = [
    'formencode',
    'pyramid',
    'pyramid_beaker',
    'pyramid_mailer',
    'pyramid_tm',
    'SQLAlchemy',
    'recaptcha-client',
    'simplejson',
    'transaction',
    'WebError',
    'webtest',
    'zope.sqlalchemy',
]
if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')


entry_points = """\
    [paste.app_factory]
    main = auth:main
"""


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()


setup(
    name='auth',
    version='0.1',
    description='auth',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Roy Hyunjin Han',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='auth',
    install_requires=requires,
    entry_points = entry_points,
    paster_plugins=['pyramid'])
