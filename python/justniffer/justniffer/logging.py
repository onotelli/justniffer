from os import environ
ENV_VARIABLE = 'LOGURU_LEVEL'
log_level = environ.get(ENV_VARIABLE, 'INFO')
environ[ENV_VARIABLE] = log_level
from loguru import logger
