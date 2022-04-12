import dataclasses
import re
import clingo
import typeguard
import valid8

from dataclass_type_validator import dataclass_type_validator, TypeValidationError
from typing import Callable, List, Iterable
from typeguard import typechecked


def validate_dataclass(data):
    try:
        dataclass_type_validator(data)
    except TypeValidationError as e:
        raise TypeError(e)


@typechecked
def pattern(regex: str) -> Callable[[str], bool]:
    r = re.compile(regex)

    def res(value):
        return bool(r.fullmatch(value))

    res.__name__ = f'pattern({regex})'
    return res


validate = valid8.validate
ValidationError = valid8.ValidationError


def on_model_print(m):
    print(m)


@typeguard.typechecked
@dataclasses.dataclass(order=True, unsafe_hash=True, frozen=True)
class Model:
    __value: List[clingo.Symbol]

    @staticmethod
    def of(model: clingo.Model):
        return Model([x for x in model.symbols(shown=True)])

    def __post_init__(self):
        validate_dataclass(self)
        self.__value.sort()

    def __str__(self):
        return ' '.join(str(x) for x in self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return self.__value.__iter__()


@typeguard.typechecked
@dataclasses.dataclass(order=True, unsafe_hash=True, frozen=True)
class ModelList:
    __value: List[Model]

    @staticmethod
    def of(models: Iterable[Model]):
        return ModelList(list(models))

    @staticmethod
    def empty():
        return ModelList([])

    def __post_init__(self):
        validate_dataclass(self)
        self.__value.sort()

    def __str__(self):
        return '-' if self.empty() else '\n'.join(str(x) for x in self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return iter(self.__value)

    def is_emtpy(self):
        return len(self.__value) == 0


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
        self.__value.append(Model.of(model))

    def __str__(self):
        return '\n'.join(str(x) for x in self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return iter(self.__value)


def do_nothing(*args):
    pass
