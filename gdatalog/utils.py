import dataclasses
from dataclasses import InitVar
from typing import List, Iterable

import typeguard
from dumbo_asp.primitives.models import Model
from valid8 import validate


def on_model_print(m):
    print(m)


@typeguard.typechecked
@dataclasses.dataclass(order=True, unsafe_hash=True, frozen=True)
class ModelList:
    __value: List[Model]
    __unexplored: bool = dataclasses.field(default=False)

    key: InitVar[object] = dataclasses.field(default=...)
    __key = object

    @staticmethod
    def of(models: Iterable[Model]):
        return ModelList(list(models), key=ModelList.__key)

    @staticmethod
    def empty():
        return ModelList([], key=ModelList.__key)

    @staticmethod
    def unexplored():
        return ModelList([], True, key=ModelList.__key)

    def __post_init__(self, key):
        validate("key", key, equals=self.__key, help_msg="ModelList must be created using the static factory methods")
        validate("unexplored", self.__unexplored and len(self.__value) > 0, equals=False, help_msg="A ModelList cannot be both unexplored and non-empty")
        self.__value.sort()

    def __str__(self):
        return '-' if self.is_emtpy() else '\n'.join(str(x) for x in self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return iter(self.__value)

    def is_emtpy(self):
        return len(self.__value) == 0

    def is_unexplored(self):
        return self.__unexplored


@typeguard.typechecked
@dataclasses.dataclass
class ModelCount:
    __value: int = dataclasses.field(default=0)

    def __call__(self, model):
        self.__value += 1

    @property
    def value(self) -> int:
        return self.__value


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class ModelCollect:
    __value: List[Model] = dataclasses.field(default_factory=list)

    def __call__(self, model):
        self.__value.append(Model.of_elements(x for x in model.symbols(shown=True)))

    def __str__(self):
        return '\n'.join(str(x) for x in self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return iter(self.__value)


def do_nothing(*_):
    pass
