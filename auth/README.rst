User account management
=======================
The user account management example demonstrates user authentication and authorization using the Pyramid web application framework. ::

    # Activate isolated environment
    source ../../bin/activate
    # Install dependencies
    python setup.py develop
    # Run tests with coverage
    nosetests
    # Show URL routes
    paster proutes development.ini auth
    # Run shell
    paster pshell development.ini auth
    # Start server
    paster serve --reload development.ini
