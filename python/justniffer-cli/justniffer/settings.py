from typing import Protocol, Literal, cast, get_args
from dynaconf import Dynaconf, Validator


Formatter = Literal['json', 'str']
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

class Settings(Protocol):
    formatter: Formatter | None 
    envvar_prefix_for_dynaconf: str
    config_file: str | None
    log_level: LogLevel

settings :Settings= cast(Settings, Dynaconf(
    envvar_prefix='JUSTNIFFER',
    settings_files=['settings.toml', 'settings.yaml'],
    validators = [Validator('formatter',  default=None),
                  Validator('log_level', is_in=get_args(LogLevel), default='INFO'),
                  Validator('config_file', default=None),
                  ]
))






