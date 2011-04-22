'Classes and functions for command-line utilities'
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.append(basePath)
import optparse
import ConfigParser
from sqlalchemy import create_engine

from auth.models import initialize_sql


class OptionParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(self)
        self.add_option('-c', '--configurationPath', dest='configurationPath', help='use the specified configuration file', metavar='PATH', default=os.path.join(basePath, 'development.ini'))
        self.add_option('-q', '--quiet', action='store_false', dest='verbose', help='be quiet', default=True)


def initialize(options):
    'Connect to database'
    if options.verbose:
        print 'Using %s' % options.configurationPath
    configuration = ConfigParser.ConfigParser({'here': basePath})
    configuration.read(options.configurationPath)
    initialize_sql(create_engine(configuration.get('app:auth', 'sqlalchemy.url')))
    return configuration
