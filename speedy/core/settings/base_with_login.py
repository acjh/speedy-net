from .base import *


LOGIN_ENABLED = True


INSTALLED_APPS += [
    'speedy.core.profiles',
    'speedy.core.im',
    'speedy.core.friends',
    'speedy.core.contact_by_form',
]

MIDDLEWARE += [
    'speedy.core.accounts.middleware.SiteProfileMiddleware',
]

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/me/'

# UNAVAILABLE_USERNAMES = [
#     'about',
#     'admin',
#     'contact',
#     'css',
#     'domain',
#     'editprofile',
#     'feedback',
#     'friends',
#     'i18n',
#     'icons',
#     'images',
#     'javascript',
#     'js',
#     'locale',
#     'login',
#     'logout',
#     'mail',
#     'me',
#     'messages',
#     'postmaster',
#     'python',
#     'register',
#     'report',
#     'resetpassword',
#     'root',
#     'setsession',
#     'speedy',
#     'speedycomposer',
#     'speedymail',
#     'speedymailsoftware',
#     'speedymatch',
#     'speedynet',
#     'static',
#     'uri',
#     'webmaster',
#     'welcome',
# ]
#
DONT_REDIRECT_INACTIVE_USER = [
    '/logout/',
    '/welcome/',
    '/registration-step-',
    '/about/',
    '/privacy/',
    '/terms/',
    '/contact/',
    '/edit-profile/',
    '/admin/',
    '/media/',
    '/static/',
    '/set-session/',
]

LOCALE_PATHS += [
    str(ROOT_DIR / 'speedy/net/locale'),
    str(ROOT_DIR / 'speedy/match/locale'),
]

