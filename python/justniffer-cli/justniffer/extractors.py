from abc import abstractmethod, ABC
from typing import Any, TypeVar, Generic

from justniffer.model import Event, Connection, ExtractorResponse

class BaseExtractor:
    @property
    def name(self) -> str:
        __name__ = self.__class__.__name__
        return __name__[0].lower()+__name__[1:]


class Extractor(ABC, BaseExtractor):

    @abstractmethod
    def value(self, connection: Connection, events: list[Event], time: float | None) -> ExtractorResponse | None: ...


class ContentExtractor(ABC, BaseExtractor):
    def get_conn_attrs(self, connection: Connection) -> Any | None:
        return connection.protocol.get(self.name, None)
    
    def set_conn_attrs(self, connection:Connection, res: Any) -> None:
        connection.protocol[self.name] = res
    
    @abstractmethod
    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ExtractorResponse | None: ...


T = TypeVar('T')
class TypedContentExtractor(Generic[T], ContentExtractor):
    def get_conn_attrs(self, connection: Connection) -> T | None:
        return connection.protocol.get(self.name, None)

    def set_conn_attrs(self, connection: Connection, res: T) -> None:
        return super().set_conn_attrs(connection, res)