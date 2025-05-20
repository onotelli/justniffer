from abc import abstractmethod, ABC
from typing import Any
from datetime import datetime
from enum import Enum
from dataclasses import is_dataclass
import json
from justniffer.class_utils import TypedPluginManager
from justniffer.model import ExtractorResponse
from justniffer.settings import settings
from justniffer.config import load_config
from justniffer.logging import logger
SEP = ' '
NULL_VALUE = '-'


def to_date_string(dt: datetime):
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def float_to_str(v: float) -> str:
    return f'{v:.4f}'


def to_str(value: Any | None) -> str:
    if value is None:
        return NULL_VALUE
    if hasattr(value, '__to_output_str__'):
        return value.__to_output_str__()
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return float_to_str(value)
    if isinstance(value, datetime):
        return to_date_string(value)
    if isinstance(value, (tuple, list, set)):
        return SEP.join(map(to_str, value))
    if isinstance(value, dict):
        return to_str(list(value.values()))
    if is_dataclass(value):
        return to_str(value.__dict__)
    else:
        return str(value)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__to_json__'):
            return o.__to_json__()
        if is_dataclass(o):
            return o.__dict__
        if isinstance(o, datetime):
            return to_str(o)
        if isinstance(o, bytes):
            return o.hex()
        if isinstance(o, Enum):
            return o.name
        return super().default(o)


def dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=4, cls=CustomJSONEncoder)


class Formatter(ABC):
    @abstractmethod
    def format(self, value: ExtractorResponse) -> str: ...


class StrFormatter(Formatter):
    def format(self, value: ExtractorResponse) -> str:
        return to_str(value)


class JSONFormatter(Formatter):
    def format(self, value: ExtractorResponse) -> str:
        return dumps(value)


FORMATTERS = {
    'json': JSONFormatter(),
    'str': StrFormatter()
}


FormatterManager = TypedPluginManager[Formatter]


class PippoFormatter(Formatter):
    def format(self, value: ExtractorResponse) -> str:
        return 'pippo'

def get_formatter() -> Formatter:
    config = load_config(settings.config_file)
    formatter_name = settings.formatter or config.formatter or 'str'
    if formatter_name in FORMATTERS:
        formatter = FORMATTERS[formatter_name]
    else:
        formatter = FormatterManager(__name__).get_class_from_name(formatter_name)()

    logger.debug(f'Formatter: {formatter}')
    return formatter
