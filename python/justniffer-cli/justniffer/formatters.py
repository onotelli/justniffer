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


def to_str(value: Any | None, *, sep: str = SEP, null_value: str = NULL_VALUE) -> str:
    if value is None:
        return null_value
    if hasattr(value, '__to_output_str__'):
        return value.__to_output_str__(sep=sep, null_value=null_value)
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return float_to_str(value)
    if isinstance(value, datetime):
        return to_date_string(value)
    if isinstance(value, (tuple, list, set)):
        return sep.join(map(lambda value: to_str(value, sep=sep, null_value=null_value), value))
    if isinstance(value, dict):
        return to_str(list(value.values()), sep=sep, null_value=null_value)
    if is_dataclass(value):
        return to_str(value.__dict__, sep=sep, null_value=null_value)
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
    def __init__(self, *, sep: str = SEP, null_value: str = NULL_VALUE):
        super().__init__()
        self.sep = sep
        self.null_value = null_value

    def format(self, value: ExtractorResponse) -> str:
        return to_str(value, sep=self.sep, null_value=self.null_value)


class JSONFormatter(Formatter):
    def format(self, value: ExtractorResponse) -> str:
        return dumps(value)


FORMATTERS = {
    'json': JSONFormatter,
    'str': StrFormatter
}


FormatterManager = TypedPluginManager[Formatter]


class PippoFormatter(Formatter):
    def format(self, value: ExtractorResponse) -> str:
        return 'pippo'


_logged = False


def get_formatter() -> Formatter:
    global _logged
    config = load_config(settings.config_file)
    formatter_def: Any = settings.formatter or config.formatter or 'str'
    formatter_args: dict = {}
    if isinstance(formatter_def, str):
        formatter_name = formatter_def
    else:
        formatter_name, formatter_args = next(iter(formatter_def .items()))

    if not _logged:
        logger.info(f'Formatter: {formatter_name} {formatter_args}')
        _logged = True
    if formatter_name in FORMATTERS:
        formatter = FORMATTERS[formatter_name](**formatter_args)
    else:
        if isinstance(formatter_def, dict):
            formatter_def = tuple(formatter_def.items())[0]
        formatter_class, kargs = FormatterManager(__name__).get_class_from_name(formatter_def)
        formatter = formatter_class(**(kargs or {}))
    logger.debug(f'Formatter: {formatter}')
    return formatter
