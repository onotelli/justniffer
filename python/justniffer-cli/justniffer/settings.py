from typing import Protocol, Literal, cast
from dynaconf import Dynaconf, Validator

Literal['json', 'str']

class Settings(Protocol):
    formatter: Literal['json', 'str']
    envvar_prefix: str

settings :Settings= cast(Settings, Dynaconf(
    envvar_prefix='JUSTNIFFER',
    settings_files=['settings.toml', 'settings.yaml'],
    validators = [Validator('formatter', is_in=['json', 'str'], default='str')]
))






