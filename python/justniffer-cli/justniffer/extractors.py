from abc import abstractmethod, ABC

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

    @abstractmethod
    def value(self, connection: Connection, events: list[Event], time: float | None, request: bytes, response: bytes) -> ExtractorResponse | None: ...
