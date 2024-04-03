
%*
connection(1,2).
connection(1,3).
connection(1,4).
connection(2,4).
connection(4,5).
*%

%*
connection(1,2).
connection(2,3).
connection(3,4).
connection(4,5).
connection(5,6).
connection(6,7).
connection(7,8).
connection(8,9).
connection(9,10).
%connection(10,1).

connection(X,Y) :- connection(Y,X).
router(X) :- connection(X,Y).


%failures(@delta(poisson(C, 5)) :- C = #count{X : router(X)}.

%{fail(X) : router(X)} = F :- failures(F).
fail(X, @delta(flip(1, 5), X)) :- router(X).
fail(X) :- fail(X,1).

reach(X) :- X = #min{Y : router(Y), not fail(Y)}.
reach(Y) :- reach(X), connection(X,Y), not fail(Y).
disconnected :- router(X), not fail(X), not reach(X).

:- not disconnected.

#show.
#show disconnected/0.
*%

%*
{foo}.
side(1, @delta(flip(1,2), 1)).
side(2, @delta(flip(1,2), 2)) :- foo.
:- side(1, F), not side(2, F).
%{foo} :- side(1, 1), side(2, 1).
*%

{play}.
win(@delta(flip(1,2), 1)) :- play.
:- play, not win(1).
play.
