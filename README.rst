Examples of simple web applications built with Pyramid
======================================================
`Pyramid <http://docs.pylonsproject.org/docs/pyramid.html>`_ is a web application framework that is the successor to `Pylons <http://pylonshq.com/>`_ and `repoze.bfg <http://bfg.repoze.org/>`_.  To run the examples, create an isolated Python environment, install Pyramid and clone the repository. 
::

    # Prepare isolated environment
    PYRAMID_ENV=$HOME/Projects/pyramid-env
    virtualenv --no-site-packages $PYRAMID_ENV 
    # Activate isolated environment
    source $PYRAMID_ENV/bin/activate
    # Install packages
    pip install ipython ipdb nose coverage
    # Clone repository
    EXAMPLES=$PYRAMID_ENV/examples
    git clone git://github.com/invisibleroads/pyramid-examples.git $EXAMPLES

For more information on running an example, please read the ``README.rst`` contained in each example's folder.
