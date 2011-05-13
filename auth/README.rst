User account management
=======================
The user account management example demonstrates user authentication and authorization using the Pyramid web application framework.
::

    # Prepare isolated environment
    PYRAMID_ENV=$HOME/Projects/pyramid-env
    virtualenv --no-site-packages $PYRAMID_ENV 
    # Activate isolated environment
    source $PYRAMID_ENV/bin/activate
    # Install packages
    pip install ipython ipdb nose coverage

    # Enter repository
    EXAMPLES=$PYRAMID_ENV/examples
    cd $EXAMPLES/auth
    # Install dependencies
    python setup.py develop

    # Edit sensitive information
    vim .test.ini
    # Run tests with coverage
    nosetests --pdb --pdb-failures
    # Show URL routes
    paster proutes development.ini auth
    # Run shell
    paster pshell development.ini auth

    # Edit sensitive information
    vim .development.ini
    # Start development server
    paster serve --reload development.ini

    # Edit sensitive information
    vim .production.ini
    # Start production server
    paster serve --daemon production.ini

    # Edit and install crontab.crt
    vim deployment/crontab.crt
    crontab deployment/crontab.crt
