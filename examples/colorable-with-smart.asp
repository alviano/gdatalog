color(red). color(green). color(blue).

% complete graph K4
node(1..4).
edge(X,Y) :- node(X), node(Y), X < Y.

removed(X,Y,@delta((5,95), X,Y)) :- edge(X,Y).

{assign(X,C) : color(C)} = 1 :- node(X).

:- edge(X,Y), not removed(X,Y,1), assign(X,C), assign(Y,C).

#show.
#show colorable.
