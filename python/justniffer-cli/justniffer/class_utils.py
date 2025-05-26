from typing import Any, Generic, TypeVar
from sys import modules
from importlib import import_module

from justniffer.logging import logger


CLASS_SEPARATOR = ':'


ClassNameDef = str | type

ClassDef = ClassNameDef | tuple[ClassNameDef, dict | None]


class PluginManager:
    _classes: dict[str, Any] = {}
    _logged: bool

    def __init__(self, module_name: str) -> None:
        self._module_name = module_name
        self._logged = False

    def get_objects(self, *class_names: ClassDef) -> tuple[Any, ...]:
        if not self._logged:
            logger.info(f'{self.__class__.__name__} {class_names}')
            self._logged = True
        logger.debug(f'{class_names=}')
        _classes = tuple(self.get_class_from_name(class_name) for class_name in class_names)
        return tuple(class_(**(kwargs or {})) for class_, kwargs in _classes)

    def get_class_from_name(self, class_name: ClassDef) -> tuple[type[Any], dict | None]:
        if isinstance(class_name, (str, tuple)):
            args: dict | None
            if isinstance(class_name, str):
                args = {}
            else:
                class_name, args = class_name
            assert isinstance(class_name, str)
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
            return self._classes[class_name], args
        else:
            assert isinstance(class_name, type)
            # logger.info(f' {class_name}')
            return class_name, {}


T = TypeVar('T')


class TypedPluginManager(Generic[T], PluginManager):
    _classes: dict[str, type[Any]] = {}

    def get_objects(self, *class_names: ClassDef) -> tuple[T, ...]:

        return super().get_objects(*class_names)

    def get_class_from_name(self, class_name: ClassDef) -> tuple[type[T], dict | None]:
        return super().get_class_from_name(class_name)
