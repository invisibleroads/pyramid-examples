Bulletin board
==============
The bulletin board example demonstrates simple view configuration using the Pyramid web application framework. ::

    # Activate isolated environment
    source ../../bin/activate
    # Install dependencies
    python setup.py develop
    # Run tests with coverage
    nosetests
    # Show URL routes
    paster proutes development.ini board
    # Run shell
    paster pshell development.ini board
    # Start server
    paster serve --reload development.ini
