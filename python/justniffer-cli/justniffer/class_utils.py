from typing import Any, Generic, TypeVar
from sys import modules
from importlib import import_module

from justniffer.logging import logger
CLASS_SEPARATOR = ':'


class PluginManager:
    _classes: dict[str, Any] = {}

    def __init__(self, module_name: str) -> None:
        self._module_name = module_name

    def get_objects(self, *class_names: str | type) -> tuple[Any, ...]:
        logger.debug(f'{class_names=}')
        _classes = tuple(self.get_class_from_name(class_name) for class_name in class_names)
        return tuple(class_() for class_ in _classes)

    def get_class_from_name(self, class_name: str | type) -> type[Any]:
        if isinstance(class_name, str):
            if class_name not in self._classes:
                logger.debug(f'finding {class_name=}')
                if CLASS_SEPARATOR in class_name:
                    module_name, class_name_ = class_name.split(CLASS_SEPARATOR)
                else:
                    class_name_ = class_name
                    module_name = self._module_name
                if module_name not in modules:
                    import_module(module_name)
                    logger.debug(f'importing {module_name}')
                class_ = getattr(modules[module_name], class_name_)
                self._classes[class_name] = class_
            return self._classes[class_name]
        else:
            return class_name


T = TypeVar('T')


class TypedPluginManager(Generic[T], PluginManager):
    _classes: dict[str, type[Any]] = {}

    def get_objects(self, *class_names: str | type) -> tuple[T, ...]:
        return super().get_objects(*class_names)

    def get_class_from_name(self, class_name: str | type) -> type[T]:
        return super().get_class_from_name(class_name)
