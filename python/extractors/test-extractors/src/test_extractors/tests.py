from justniffer.extractors import Extractor, Connection, Event, ExtractorResponse

class TestExtractor(Extractor):
    def value(self, connection: Connection, events: list[Event], time: float | None) -> ExtractorResponse | None:
        return 'test'
