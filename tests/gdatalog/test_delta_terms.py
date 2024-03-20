import clingo
import pytest

from dumbo_utils.validation import ValidationError

from gdatalog import utils
from gdatalog.delta_terms import DeltaTermsContext, flip, binom, poisson, small


def test_flip_bias_cannot_be_less_than_zero():
    with pytest.raises(ValidationError):
        flip(clingo.Number(-1), clingo.Number(10))


def test_flip_bias_cannot_be_greater_than_one():
    with pytest.raises(ValidationError):
        flip(clingo.Number(3), clingo.Number(2))


def test_flip_bias_must_be_a_number():
    with pytest.raises(ValidationError):
        flip(clingo.Number(1), clingo.Number(0))


def test_flip_single_coin():
    ctl = clingo.Control()
    ctl.configuration.solve.models = 0
    ctl.add("base", [], """
res(@delta(flip, (1,2), (a))).
    """)
    ctl.ground([("base", [])], context=DeltaTermsContext())
    model_count = utils.ModelCount()
    res = ctl.solve(on_model=model_count)
    assert res.satisfiable
    assert model_count.value == 1


def test_binom():
    expected = [
        0.07775999999999998,
        0.2592000000000001,
        0.34559999999999974,
        0.23039999999999994,
        0.0768,
    ]
    for _ in range(10):
        res = binom(clingo.Number(5), clingo.Number(4), clingo.Number(10))
        assert float(res[1]) == pytest.approx(expected[res[0].number])


def test_poisson():
    expected = [
        0.5488116360940265,
        0.3292869816564159,
        0.09878609449692473,
    ]
    for _ in range(1000):
        res = poisson(clingo.Number(6), clingo.Number(10))
        if res[0].number < len(expected):
            assert float(res[1]) == pytest.approx(expected[res[0].number])
        else:
            assert float(res[1]) <= 0.02


def test_small():
    res = small(clingo.Number(1), clingo.Number(1))
    assert res[0].number in [0, 1]
