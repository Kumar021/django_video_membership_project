import os
import django_heroku
import dj_database_url
from decouple import config

django_heroku.settings(locals(), staticfiles=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG")
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'dj-video-demo.herokuapp.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', #whitenoise
    'django.contrib.staticfiles',
    
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'courses',
    'memberships'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'videoservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates', 'allauth')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'videoservice.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<database_name>',
        'USER': '<user_name>',
        'PASSWORD': '<password>',
        'HOST': 'localhost',
        'PORT': '',
    }
}

WHITENOISE_USE_FINDERS = True

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_root'), ]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

VENV_PATH = os.path.dirname(BASE_DIR)

MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(VENV_PATH, 'media_root')
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


if DEBUG:
    STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")

else:
    # live keys
    STRIPE_PUBLISHABLE_KEY = ''
    STRIPE_SECRET_KEY = ''


# Django allauth

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


SITE_ID = 1

ACCOUNT_ADAPTER = 'courses.adapter.AccountAdapter'
LOGIN_REDIRECT_URL = '/memberships'
ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_FORMS = {
   'login': 'courses.forms.MyCustomLoginForm',
   'signup': 'courses.forms.MyCustomSignupForm'
}


#STATICFILES_STORAGE = 'whitenoise.django.CompressedManifestStaticFilesStorage'