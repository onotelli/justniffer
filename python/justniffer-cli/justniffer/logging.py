from os import environ
from justniffer.settings import settings
ENV_VARIABLE = 'LOGURU_LEVEL'

log_level = settings.log_level
environ[ENV_VARIABLE] = log_level
from loguru import logger
