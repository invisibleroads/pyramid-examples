Examples of simple web applications built with Pyramid
======================================================
`Pyramid <http://docs.pylonsproject.org/docs/pyramid.html>`_ is a web application framework that is the successor to `Pylons <http://pylonshq.com/>`_ and `repoze.bfg <http://bfg.repoze.org/>`_.  To run the examples, create an isolated Python environment, install Pyramid and clone the repository. ::

    virtualenv --no-site-packages pyramid-env
    cd pyramid-env
    source bin/activate
    pip install pyramid ipython coverage
    git clone git://github.com/invisibleroads/pyramid-examples.git examples
