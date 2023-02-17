import dataclasses
from collections import defaultdict
from dataclasses import InitVar
from typing import List, Dict, Optional
from dumbo_utils.validation import validate

import clingo
import typeguard

from gdatalog import utils
from gdatalog.delta_terms import DeltaTermsContext, DeltaTermCall, Probability
from gdatalog.utils import ModelList


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class SmsResult:
    state: clingo.SolveResult
    models: ModelList
    delta_terms: List[DeltaTermCall]
    delta_terms_key: str

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
    __delta_terms_to_sms_result: Dict[str, SmsResult] = dataclasses.field(default_factory=dict)

    def sms(self, delta_terms_key: Optional[str] = None) -> SmsResult:
        if delta_terms_key is not None:
            return self.__delta_terms_to_sms_result[delta_terms_key]

        context = DeltaTermsContext()
        model_collect = utils.ModelCollect()

        control = clingo.Control()
        control.configuration.solve.models = self.max_stable_models
        control.add("base", [], self.code)
        control.ground([("base", [])], context=context)

        delta_terms = str(sorted(context.calls))
        if delta_terms not in self.__delta_terms_to_sms_result:
            res = control.solve(on_model=model_collect)
            self.__delta_terms_to_sms_result[delta_terms] = SmsResult(
                state=res,
                models=ModelList.of(x for x in model_collect),
                delta_terms=context.calls,
                delta_terms_key=delta_terms,
            )
        return self.__delta_terms_to_sms_result[delta_terms]


@typeguard.typechecked
@dataclasses.dataclass()
class Repeat:
    program: Program
    number_of_calls: int
    counters: Dict[str, int]
    key: InitVar[object]

    __key = object()

    def __post_init__(self, key):
        validate('key', key, equals=self.__key, help_msg="Must be created by Repeat::on()")

    @classmethod
    def on(cls, program: Program, times: int) -> 'Repeat':
        validate('times', times, min_value=1)
        counters = defaultdict(lambda: 0)
        for _ in range(times):
            res = program.sms()
            counters[res.delta_terms_key] += 1
        return Repeat(program=program, number_of_calls=times, counters=counters, key=cls.__key)

    def repeat(self, times: int):
        validate('times', times, min_value=1)
        self.number_of_calls += times
        for _ in range(times):
            res = self.program.sms()
            self.counters[res.delta_terms_key] += 1

    def no_stable_model_frequency(self):
        freq = Probability()
        for key in self.counters:
            res = self.program.sms(key)
            if res.models.is_emtpy():
                freq += Probability.of(self.counters[key], self.number_of_calls)
        return freq

    def sets_of_stable_models_frequency(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(key)
            models_as_str = str(res.models)
            frequency[models_as_str] += Probability.of(self.counters[key], self.number_of_calls)
            models[models_as_str] = res.models
        return SetsOfStableModelsFrequency(frequency, models)

    def stable_models_frequency_under_uniform_distribution(self):
        frequency = defaultdict(lambda: Probability())
        models = {}
        for key in self.counters:
            res = self.program.sms(key)
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
