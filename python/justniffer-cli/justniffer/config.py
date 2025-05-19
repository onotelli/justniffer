from pydantic import BaseModel
from functools import cache
import yaml
from justniffer.logging import logger

class Config(BaseModel):
    selectors: tuple[str, ...] | None = None
    extractors: tuple[str, ...] | None = None
    formatter: str | None = None


@cache
def load_config(filepath: str | None) -> Config:
    logger.debug(f'load_config {filepath=}')
    if filepath is None:
        return Config()
    else:
        with open(filepath, 'r') as f:
            obj = yaml.safe_load(f)
        return Config.model_validate(obj)
