from typing import Protocol, Literal, cast, get_args
from dynaconf import Dynaconf, Validator


Formatter = Literal['json', 'str']
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

class Settings(Protocol):
    formatter: Formatter
    envvar_prefix: str
    config_file: str | None
    log_level: LogLevel

settings :Settings= cast(Settings, Dynaconf(
    envvar_prefix='JUSTNIFFER',
    settings_files=['settings.toml', 'settings.yaml'],
    validators = [Validator('formatter', is_in=get_args(Formatter), default='str'),
                  Validator('log_level', is_in=get_args(LogLevel), default='INFO'),
                  Validator('config_file', default=None),
                  ]
))






