Bulletin board
==============
The bulletin board example demonstrates simple view configuration using the Pyramid web application framework. 
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
    git clone git://github.com/invisibleroads/pyramid-examples.git $EXAMPLES
    cd $EXAMPLES/board
    # Install dependencies
    python setup.py develop

    # Run tests with coverage
    nosetests --pdb --pdb-failures
    # Show URL routes
    paster proutes development.ini board
    # Run shell
    paster pshell development.ini board

    # Start server
    paster serve --reload development.ini
