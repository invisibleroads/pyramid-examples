# fix login
# fix logout
# fix index
# fix register and register_
# fix confirm and confirm_
# fix update and update_
# fix datetime format for /users
# fix reset
# fix whenIO to use pytz and display timezone
# add salt to store in db
# consider overwriting AuthTktAuthenticationPolicy
# add CSRF to account update
'Pyramid WSGI configuration'
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings

from auth.views import users


    # Configure sessions and caching
    if 'session.secret' not in settings:
        settings['session.secret'] = make_random_string(32)
    config.set_session_factory(session_factory_from_settings(settings))
    set_cache_regions_from_settings(settings)
    # Configure mailer
    config.include('pyramid_mailer')
    # Configure routes for user account management
    config.scan(users)
    config.include(users.add_routes)
