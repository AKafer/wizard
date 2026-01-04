import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Security
SECRET_KEY = os.getenv('SECRET_KEY')

# File paths
STATIC_FOLDER = 'static'

# Database
DATABASE_POOL_SIZE = os.getenv('DB_POOL_SIZE', default=20)
DATABASE_POOL_MAX_OVERFLOW = os.getenv('DB_POOL_MAX_OVERFLOW', default=5)
DATABASE_HOST = os.getenv('DB_HOST', default='localhost')
DATABASE_PORT = os.getenv('DB_PORT', default=5432)
DATABASE_NAME = os.getenv('POSTGRES_DB', default='')
DATABASE_USER = os.getenv('POSTGRES_USER', default='')
DATABASE_PASSWORD = os.getenv('POSTGRES_PASSWORD', default='')
DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

# Superuser
SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD')
SUPERUSER_NAME = os.getenv('SUPERUSER_NAME')
SUPERUSER_LAST_NAME = os.getenv('SUPERUSER_LAST_NAME')

# CORS
ORIGIN_HOSTS = os.getenv('ORIGIN_HOSTS', '').split(',')

# Redis
REDIS_URL = os.getenv('REDIS_URL', default='redis://localhost:6379/0')

# Logging
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

# Rate Limiter
RATE_LIMITER_TIMES = int(os.getenv('RATE_LIMITER_TIMES', default=5))
RATE_LIMITER_SECONDS = int(os.getenv('RATE_LIMITER_SECONDS', default=10))

# Kafka
KAFKA_BOOTSTRAP_HOST = os.getenv('KAFKA_BOOTSTRAP_HOST', default='localhost')
KAFKA_BOOTSTRAP_PORT = os.getenv('KAFKA_BOOTSTRAP_PORT', default=9092)
KAFKA_GROUP_ID = 'wizard_consumer_group'
KAFKA_SMS_TOPIC = 'sms_topic'


# API clients
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60

# Failsafe
FAILSAFE_ALLOWED_RETRIES: int = 3
FAILSAFE_BACKOFF_SECONDS: float = 0.2

# MTS API
MTS_LOGIN = os.getenv('MTS_LOGIN')
MTS_PASSWORD = os.getenv('MTS_PASSWORD')
MTS_NAME = os.getenv('MTS_NAME')
SMS_TEXT = os.getenv('SMS_TEXT')
MTS_BASE_URL = 'https://omnichannel.mts.ru'
MTS_SEND_MSG_URL = '/http-api/v1/messages'
MTS_CHECK_MSG_URL = '/http-api/v1/messages/info'
MTS_CHECK_BALANCE_URL = '/http-api/v1/messages/balanceManagement/balance/full'
MTS_CHECK_ATTEMPTS = 5
MTS_CHECK_BASE_DELAY = 5  # seconds
MTS_CHECK_MAX_DELAY = 3600  # seconds
MTS_SMS_TEXT_TEMPLATE = '''
По вашему подарочному сертификату {code} произошло списание на сумму {charge_sum} рублей.
Текущий баланс сертификата: {balance} рублей. Статус сертификата: {status}.
Спасибо, что выбираете нас!
'''
