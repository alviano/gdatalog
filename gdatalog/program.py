import dataclasses
from collections import defaultdict
from dataclasses import InitVar
from functools import reduce
from typing import Dict, Optional

import clingo
import typeguard
from dumbo_utils.validation import validate

from gdatalog import utils
from gdatalog.delta_terms import DeltaTermsContext, DeltaTermCall, Probability
from gdatalog.utils import ModelList


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class SmsResult:
    state: clingo.SolveResult
    models: ModelList
    delta_terms: tuple[DeltaTermCall, ...]

    def print(self):
        if self.state.satisfiable:
            print('Models:')
            print(self.models)
            print('Delta terms:')
            for term in self.delta_terms:
                print(term)


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class SetsOfStableModelsFrequency:
    __frequency: Dict[str, Probability]
    __models: Dict[str, ModelList]

    def __post_init__(self):
        validate('same_keys', self.__frequency.keys(), equals=self.__models.keys())

    def __getitem__(self, item):
        return self.__frequency[item], self.__models[item]

    def __len__(self):
        return len(self.__frequency)

    def keys(self):
        return self.__frequency.keys()

    def values(self):
        for key in self.keys():
            yield self[key]

    def frequency(self, key):
        return self.__frequency[key]

    def models(self, key):
        return self.__models[key]

    def print(self):
        print('*** Stats ***')
        for x in self.values():
            print(f'Probability: {x[0]}')
            print(f'  Models: {len(x[1])}')
            for i in range(len(x[1])):
                print(f'  Model: {x[1][i]}')


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class Program:
    code: str
    max_stable_models: int = dataclasses.field(default=0)
    __delta_terms_to_sms_result: Dict[tuple[DeltaTermCall, ...], SmsResult] = dataclasses.field(default_factory=dict)

    def sms(self, *, delta_terms: Optional[tuple[DeltaTermCall, ...]] = None,
            calls_prefixes: Optional[dict[tuple[DeltaTermCall, ...], set[clingo.Symbol]]] = None) -> SmsResult:
        if delta_terms is not None:
            return self.__delta_terms_to_sms_result[delta_terms]

        context = DeltaTermsContext(calls_prefixes)
        model_collect = utils.ModelCollect()

        control = clingo.Control()
        control.configuration.solve.models = self.max_stable_models
        control.add("base", [], self.code)
        control.ground([("base", [])], context=context)

        delta_terms = context.calls
        if delta_terms not in self.__delta_terms_to_sms_result:
            res = control.solve(on_model=model_collect)
            self.__delta_terms_to_sms_result[delta_terms] = SmsResult(
                state=res,
                models=ModelList.of(x for x in model_collect),
                delta_terms=delta_terms,
            )
        return self.__delta_terms_to_sms_result[delta_terms]


@typeguard.typechecked
@dataclasses.dataclass()
class Repeat:
    program: Program
    number_of_calls: int
    counters: Dict[tuple[DeltaTermCall, ...], int]
    key: InitVar[object]

    __key = object()

    def __post_init__(self, key):
        validate('key', key, equals=self.__key, help_msg="Must be created by Repeat::on()")

    @classmethod
    def on(cls, program: Program, times: Optional[int] = None) -> 'Repeat':
        res = Repeat(program=program, number_of_calls=0, counters=defaultdict(lambda: 0), key=cls.__key)
        if times is not None:
            validate('times', times, min_value=1)
            res.repeat(times)
        return res

    def repeat(self, times: int):
        validate('times', times, min_value=1)
        self.number_of_calls += times
        for _ in range(times):
            res = self.program.sms()
            self.counters[res.delta_terms] += 1

    def no_stable_model_frequency(self):
        freq = Probability()
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            if res.models.is_emtpy():
                freq += Probability.of(self.counters[key], self.number_of_calls)
        return freq

    def sets_of_stable_models_frequency(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            models_as_str = str(res.models)
            frequency[models_as_str] += Probability.of(self.counters[key], self.number_of_calls)
            models[models_as_str] = res.models
        return SetsOfStableModelsFrequency(frequency, models)

    def stable_models_frequency_under_uniform_distribution(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            if res.models:
                for model in res.models:
                    model_as_str = str(model)
                    frequency[model_as_str] += Probability.of(self.counters[key],
                                                              len(res.models) * self.number_of_calls)
                    models[model_as_str] = ModelList.of([model])
            else:
                frequency['INCOHERENT'] += Probability.of(self.counters[key], self.number_of_calls)
                models['INCOHERENT'] = ModelList.of([])
        return SetsOfStableModelsFrequency(frequency, models)


@typeguard.typechecked
@dataclasses.dataclass()
class SmallRepeat:
    program: Program
    number_of_calls: int
    counters: Dict[tuple[DeltaTermCall, ...], int]
    key: InitVar[object]
    __calls_prefixes: Dict[tuple[DeltaTermCall, ...], set[clingo.Symbol]] = dataclasses.field(
        default_factory=dict, init=False)

    __key = object()

    def __post_init__(self, key):
        validate('key', key, equals=self.__key, help_msg="Must be created by Repeat::on()")

    @classmethod
    def on(cls, program: Program, times: Optional[int] = None) -> 'SmallRepeat':
        res = SmallRepeat(program=program, number_of_calls=0, counters=defaultdict(lambda: 0), key=cls.__key)
        if times is not None:
            validate('times', times, min_value=1)
            res.repeat(times)
        return res

    def repeat(self, times: int) -> bool:
        validate('times', times, min_value=1)
        self.number_of_calls += times
        for index in range(times):
            res = self.program.sms(calls_prefixes=self.__calls_prefixes)
            self.counters[res.delta_terms] += 1
            assert self.counters[res.delta_terms] == 1  # we cannot encounter the same ground program twice
            if res.delta_terms and res.delta_terms[-1].function == 'small':
                last = len(res.delta_terms)
                while last > 0 and res.delta_terms[last - 1].all_done:
                    last -= 1
                if last == 0:
                    self.number_of_calls -= times
                    self.number_of_calls += index + 1
                    return True
                key = res.delta_terms[:last - 1]
                if key not in self.__calls_prefixes:
                    self.__calls_prefixes[key] = set()
                self.__calls_prefixes[key].add(res.delta_terms[last - 1].result)
        return True

    def no_stable_model_frequency(self):
        freq = Probability()
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            if res.models.is_emtpy():
                freq += reduce(lambda p, d: p * d.probability, res.delta_terms, Probability.of(1, 1))
        return freq

    def sets_of_stable_models_frequency(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            models_as_str = str(res.models)
            frequency[models_as_str] += reduce(lambda p, d: p * d.probability, res.delta_terms, Probability.of(1, 1))
            models[models_as_str] = res.models
        return SetsOfStableModelsFrequency(frequency, models)

    def stable_models_frequency_under_uniform_distribution(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(delta_terms=key)
            if res.models:
                for model in res.models:
                    model_as_str = str(model)
                    frequency[model_as_str] += reduce(
                        lambda p, d: p * d.probability, res.delta_terms, Probability.of(1, 1)
                    )
                    models[model_as_str] = ModelList.of([model])
            else:
                frequency['INCOHERENT'] += reduce(lambda p, d: p * d.probability, res.delta_terms, Probability.of(1, 1))
                models['INCOHERENT'] = ModelList.of([])
        return SetsOfStableModelsFrequency(frequency, models)
