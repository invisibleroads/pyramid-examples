from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from auth.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'auth:static')
    config.add_route('home', '/', view='auth.views.my_view',
                     view_renderer='templates/mytemplate.pt')
    return config.make_wsgi_app()


