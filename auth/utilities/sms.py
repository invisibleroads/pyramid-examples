'Command-line script to process SMS messages'
import script_process
from auth.libraries import sms


def run(settings):
    'Connect to IMAP server and process messages'
    countByKey = sms.process(settings)
    return '\n'.join('%s: %s' % (key.capitalize(), count) for key, count in countByKey.iteritems())


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.OptionParser()
    options = optionParser.parse_args()[0]
    # Run
    message = run(script_process.initialize(options))
    # Say
    if options.verbose:
        print message
