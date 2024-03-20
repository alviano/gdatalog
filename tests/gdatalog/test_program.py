import pytest

from gdatalog.delta_terms import Probability
from gdatalog.program import Program, Repeat


def test_flip_single_coin():
    program = Program("res(@delta(flip, (1,2), ())).")
    res = program.sms()
    assert res.state.satisfiable
    assert len(res.delta_terms) == 1


def test_flip_two_coins():
    program = Program("""
res(a, @delta(flip, (1,2), (a))).
res(b, @delta(flip, (1,2), (b))).
    """)
    res = program.sms()
    # print()
    # res.print()
    assert res.state.satisfiable
    assert len(res.delta_terms) == 2


def test_same_flip_in_multiple_lines():
    program = Program("""
res(a, @delta(flip, (1,2), (a))).
res(b, @delta(flip, (1,2), (a))).
    """)
    res = program.sms()
    # print()
    # res.print()
    assert res.state.satisfiable
    assert len(res.delta_terms) == 1


def test_flip_conditional():
    program = Program("""
res(a, @delta(flip, (1,2), (a))).
res(b, @delta(flip, (1,2), (b))) :- res(a, 1).
    """)
    res = Repeat.on(program, 100)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 3
    # freq.print()


def test_flip_conditional_with_negation():
    program = Program("""
group1(a).
group1(b).
group2(c).
res1(C, @delta(flip, (1,2), (C))) :- group1(C).
some1 :- res1(C,1).
res2(C, @delta(flip, (1,2), (C))) :- group2(C), not some1.
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 5
    # freq.print()


def test_flip_conditional_with_projection():
    program = Program("""
group1(a).
group1(b).
group2(c).
res1(C, @delta(flip, (1,2), (C))) :- group1(C).
res2(C, @delta(flip, (1,2), (C))) :- group2(C), not res1(_,1).
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 5
    # freq.print()


def test_flip_conditional_with_conditional_literal():
    program = Program("""
group1(a).
group1(b).
group2(c).
res1(C, @delta(flip, (1,2), (C))) :- group1(C).
res2(C, @delta(flip, (1,2), (C))) :- group2(C); res1(C',0) : group1(C').
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 5
    # freq.print()


def test_flip_conditional_with_aggregates():
    program = Program("""
group1(a).
group1(b).
group2(c).
res1(C, @delta(flip, (1,2), (C))) :- group1(C).
res2(C, @delta(flip, (1,2), (C))) :- group2(C), #count{C' : res1(C',0)} = 0.
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 5
    # freq.print()


def test_flip_bias():
    program = Program("""
result(C, @delta(flip, (1,10), (C,))) :- C = 1..1000.

#show.
#show (F,S) : F = 0..1, S = #count{C : result(C,F)}.
    """)
    res = program.sms()
    assert res.state.satisfiable
    assert len(res.delta_terms) == 1000
    assert len(res.models) == 1
    prob = {x.arguments[0].number: x.arguments[1].number for x in res.models[0]}
    assert prob[0] + prob[1] == 1000
    assert prob[1] / 1000 == pytest.approx(0.1, rel=2)


def test_repeat_flip_coin():
    program = Program("""
#show X : X = @delta(flip, (9,10), ()).    
    """)
    res = Repeat.on(program, 1000)
    for key in res.counters:
        assert len(program.sms(key).models) == 1
        assert len(program.sms(key).models[0]) == 1
        face = program.sms(key).models[0][0]
        if face == 1:
            assert res.counters[key] / 1000 == pytest.approx(9 / 10, rel=2)


def test_program_with_multiple_stable_models():
    program = Program("""
{a; b; c} = 1.

f(a, @delta(flip, (1,2), (a))) :- a.
f(b, @delta(flip, (1,2), (b))) :- b.
f(c, @delta(flip, (1,2), (c))) :- c.

:- a, f(a, 0).
:- b, f(b, 0).
:- c, f(c, 0).
f(a, @delta(flip, (1,2), (a))) :- c, f(c, 1).
:- c, f(a, 1).

:- f(a, 1), f(b, 0).    
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 6
    # freq.print()

    freq = res.stable_models_frequency_under_uniform_distribution()
    assert len(freq) == 4
    # freq.print()


def test_program_with_randint():
    program = Program("""
res(@delta(randint, (1, 10), ())).
        """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 10
    # freq.print()


def test_program_with_binom():
    program = Program("""
res(@delta(binom, (5, 4,10), ())).    
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 6
    # freq.print()


def test_program_with_poisson():
    program = Program("""
res(@delta(poisson, (6,10), ())).    
    """)
    res = Repeat.on(program, 1000)
    freq = res.sets_of_stable_models_frequency()
    freq = [x for x in freq.values() if float(x[0]) >= 0.05]
    assert len(freq) == 3
    # freq.print()


def test_program_graph_col():
    program = Program("""
color(red). color(green). color(blue).
edge(a,b).
edge(a,c).
edge(a,d).
edge(b,c).
edge(b,d).
edge(c,d).

node(X) :- edge(X,_).
node(Y) :- edge(_,Y).

removed(X,Y,@delta(flip, (5,100), (X,Y))) :- edge(X,Y).

%{assign(X,C) : color(C)} = 1 :- node(X).
assign(X,red) :- node(X), not assign(X,green), not assign(X,blue). 
assign(X,green) :- node(X), not assign(X,red), not assign(X,blue). 
assign(X,blue) :- node(X), not assign(X,red), not assign(X,green).
 
:- edge(X,Y), not removed(X,Y,1), assign(X,C), assign(Y,C).
    """, max_stable_models=1)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    # print(freq.complement())
    assert Probability.of(2, 10) <= freq.complement() <= Probability.of(3, 10)
    # freq = res.sets_of_stable_models_frequency()
    # print(freq.keys())
    # freq.print()


def test_program_random_walk():
    program = Program("""
neighbors(a,3).
neighbor(a,1,b).
neighbor(a,2,c).
neighbor(a,3,d).

neighbors(b,3).
neighbor(b,1,a).
neighbor(b,2,c).
neighbor(b,3,d).

neighbors(c,3).
neighbor(c,1,a).
neighbor(c,2,b).
neighbor(c,3,d).

neighbors(d,3).
neighbor(d,1,a).
neighbor(d,2,b).
neighbor(d,3,c).

from(a).
to(d).

node(X) :- neighbors(X,_).

reach(X) :- from(X).
next(X,@delta(randint, (1,N), (X))) :- reach(X), not to(X), neighbors(X,N).
reach(Y) :- reach(X), next(X,I), neighbor(X,I,Y).

:- node(X), not reach(X).
    """, max_stable_models=1)
    res = Repeat.on(program, 1000)
    # freq = res.sets_of_stable_models_frequency()
    # freq.print()
    freq = res.no_stable_model_frequency()
    # print(freq.complement())
    assert Probability.of(5, 100) <= freq.complement() <= Probability.of(10, 100)


def test_program_virus_spread():
    program = Program("""
edge(a,b).
edge(a,c).
edge(a,d).
edge(b,c).
edge(c,d).
edge(Y,X) :- edge(X,Y).

node(X) :- edge(X,_).
node(Y) :- edge(_,Y).

infected(a).

infected(Y,@delta(flip, (5,100), (X,Y))) :- infected(X), edge(X,Y).
infected(X) :- infected(X,1).

healthy(X) :- node(X), not infected(X).

not_first(X) :- healthy(X), healthy(Y), X > Y.
reach(X) :- healthy(X), not not_first(X).
reach(Y) :- reach(X), edge(X,Y), healthy(Y).

:- node(X), healthy(X), not reach(X).
    """, max_stable_models=1)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    print(freq.complement())
    # assert Probability.of(2, 10) <= freq.complement() <= Probability.of(3, 10)
    freq = res.sets_of_stable_models_frequency()
    freq.print()


def test_flip_coin_then_derive_a_or_b():
    program = Program("""
coin(@delta(flip, (1,2), ())).
a :- coin(0).
b :- coin(1).    
    """)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    assert freq == Probability()
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 2
    freq.print()
    for x in freq.keys():
        assert len(freq.models(x)) == 1


def test_flip_coin_then_kill_or_derive_a_and_b():
    program = Program("""
coin(@delta(flip, (1,2), ())).
:- coin(0).
a :- coin(1), not b.
b :- coin(1), not a. 
    """)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    assert Probability.of(4, 10) <= freq <= Probability.of(6, 10)
    freq = res.sets_of_stable_models_frequency()
    assert len(freq) == 2
    freq.print()
    for x in freq.keys():
        assert len(freq.models(x)) in {0, 2}


def test_program_virus_spread_2():
    program = Program("""
connection(a,b).
connection(a,c).
connection(b,c).
connection(Y,X) :- connection(X,Y).

router(X) :- connection(X,_).

infected(a,1).

infected(Y,@delta(flip, (10,100), (X,Y))) :- infected(X,1), connection(X,Y).

healthy(X) :- router(X), not infected(X,1).

:- healthy(X), healthy(Y), connection(X,Y).
    """, max_stable_models=1)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    print(freq.complement())
    # assert Probability.of(2, 10) <= freq.complement() <= Probability.of(3, 10)
    freq = res.sets_of_stable_models_frequency()
    freq.print()


def test_program_with_small_delta():
    program = Program("""
res(@delta(small, (1,1,2), ())).
:- res(2).
    """, max_stable_models=1)
    res = Repeat.on(program, 1000)
    freq = res.no_stable_model_frequency()
    assert Probability.of(4, 10) <= freq <= Probability.of(6, 10)
    freq = res.sets_of_stable_models_frequency()
    freq.print()
