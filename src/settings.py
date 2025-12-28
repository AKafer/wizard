import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_POOL_SIZE = os.getenv('DB_POOL_SIZE', default=20)
DATABASE_POOL_MAX_OVERFLOW = os.getenv('DB_POOL_MAX_OVERFLOW', default=5)
DATABASE_HOST = os.getenv('DB_HOST', default='localhost')
DATABASE_PORT = os.getenv('DB_PORT', default=5432)
DATABASE_NAME = os.getenv('POSTGRES_DB', default='')
DATABASE_USER = os.getenv('POSTGRES_USER', default='')
DATABASE_PASSWORD = os.getenv('POSTGRES_PASSWORD', default='')
DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

STATIC_FOLDER = 'static'

ORIGIN_HOSTS = os.getenv('ORIGIN_HOSTS', '').split(',')

REDIS_URL = os.getenv('REDIS_URL', default='redis://localhost:6379/0')

LOG_HANDLERS = ['console', 'file']
LOG_LEVEL = os.getenv('LOG_LEVEL', default='DEBUG')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'logging.Formatter',
            'format': (
                '%(levelname)s [%(asctime)s] [%(name)s] %(filename)s:%(lineno)s %(message)s'
            ),
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 1,
            'encoding': 'utf8',
        },
    },
    'loggers': {
        'wizard': {
            'level': LOG_LEVEL,
            'handlers': LOG_HANDLERS,
            'propagate': False,
        },
    },
}