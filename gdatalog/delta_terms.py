import dataclasses
import random
from bisect import bisect_right
from fractions import Fraction
from functools import lru_cache
from typing import List, Any, Tuple, Iterable, Optional
from dumbo_utils.validation import validate

import clingo
from scipy import stats
from typeguard import typechecked


@typechecked
@dataclasses.dataclass(order=True, frozen=True)
class Probability:
    value: Fraction = dataclasses.field(default=Fraction(0))

    @staticmethod
    def validate(n: int, d: int):
        validate('n', n, min_value=0, max_value=d)
        validate('d', d, min_value=1)

    @staticmethod
    def of(n, d):
        return Probability(Fraction(n, d))

    def __post_init__(self):
        self.validate(self.value.numerator, self.value.denominator)

    def __str__(self):
        return f'{self.value} (~{float(self)})'

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        return Probability(self.value + other.value)

    def __mul__(self, other):
        return Probability(self.value * other.value)

    def complement(self):
        return Probability(Fraction(1) - self.value)


@typechecked
@dataclasses.dataclass(order=True, frozen=True)
class DeltaTermCall:
    function: str
    params: tuple[clingo.Symbol, ...]
    signature: tuple[clingo.Symbol, ...]
    result: Any
    probability: Probability
    all_done: bool = dataclasses.field(default=False, compare=False, hash=False)

    def __str__(self):
        params = ','.join([str(p) for p in self.params])
        signature = ','.join([str(s) for s in self.signature])
        return f'@{self.function}<{params}>({signature}) = {self.result} [{self.probability}]'


class DeltaTermsContext:
    __delta_terms = {}

    def __init__(self, calls_prefixes: Optional[dict[tuple[DeltaTermCall, ...], set[int]]] = None):
        self.__calls = []
        self.calls_prefixes = calls_prefixes or {}  # shared object

    @classmethod
    def register(cls, name, code):
        cls.__delta_terms[name] = code

    @property
    def calls(self) -> tuple[DeltaTermCall, ...]:
        return tuple(self.__calls)

    @lru_cache(maxsize=None)
    def delta(self, function, params, signature):
        if signature.type != clingo.SymbolType.Function or signature.name != '':
            signature = clingo.Function(name='', arguments=[signature])
        if function.name == 'small':
            result, probability, all_done = small(
                *params.arguments,
                disallow_list=self.calls_prefixes[self.calls] if self.calls in self.calls_prefixes else ()
            )
        else:
            result, probability = self.__delta_terms[function.name](*params.arguments)
            all_done = False
        self.__calls.append(
            DeltaTermCall(
                function=function.name,
                params=tuple(params.arguments),
                signature=tuple(signature.arguments),
                result=result,
                probability=probability,
                all_done=all_done,
            )
        )
        return result


@typechecked
def flip(bias_n: clingo.Number, bias_d: clingo.Number) -> Tuple[clingo.Number, Probability]:
    n, d = bias_n.number, bias_d.number
    Probability.validate(n, d)
    probability_of_1 = Probability.of(n, d)
    res = 1 if (random.uniform(0, 1) * d <= n) else 0
    prob = probability_of_1 if res == 1 else probability_of_1.complement()
    return clingo.Number(res), prob


@typechecked
def randint(a: clingo.Number, b: clingo.Number) -> Tuple[clingo.Number, Probability]:
    a, b = a.number, b.number
    validate('a', a)
    validate('b', b, min_value=a)
    res = random.randint(a, b)
    prob = Probability.of(1, b - a + 1)
    return clingo.Number(res), prob


@typechecked
def binom(n_classes: clingo.Number, p_numerator: clingo.Number, p_denominator: clingo.Number) -> \
        Tuple[clingo.Number, Probability]:
    n, p_n, p_d = n_classes.number, p_numerator.number, p_denominator.number
    validate('n_classes', n, min_value=1)
    Probability.validate(p_n, p_d)
    res = stats.binom.rvs(n, p_n / p_d)
    prob = Probability(Fraction.from_float(stats.binom.pmf(res, n, p_n / p_d)))
    return clingo.Number(res), prob


@typechecked
def poisson(lambda_n: clingo.Number, lambda_d: clingo.Number) -> Tuple[clingo.Number, Probability]:
    n, d = lambda_n.number, lambda_d.number
    validate('lambda_n', n, min_value=1)
    validate('lambda_d', d, min_value=1)
    res = stats.poisson.rvs(n / d)
    prob = Probability(Fraction.from_float(stats.poisson.pmf(res, n / d)))
    return clingo.Number(res), prob


@typechecked
def small(*args: clingo.Number, disallow_list: Iterable[int] = ()) -> Tuple[clingo.Number, Probability, bool]:
    bias = [arg.number for arg in args]
    allowed_list = []
    cumulative_bias = [0]
    for index, b in enumerate(bias):
        if index not in disallow_list:
            allowed_list.append(index)
            cumulative_bias.append(cumulative_bias[-1] + b)
    sum_bias = cumulative_bias[-1]
    rand = random.randint(0, sum_bias - 1)
    res = bisect_right(cumulative_bias, rand, 0, len(cumulative_bias)) - 1
    res = allowed_list[res]
    return clingo.Number(res), Probability.of(bias[res], sum(bias)), len(allowed_list) == 1


DeltaTermsContext.register('flip', flip)
DeltaTermsContext.register('randint', randint)
DeltaTermsContext.register('binom', binom)
DeltaTermsContext.register('poisson', poisson)
DeltaTermsContext.register('small', small)
