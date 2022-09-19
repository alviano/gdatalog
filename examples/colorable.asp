color(red). color(green). color(blue).

% complete graph K4
node(1..4).
edge(X,Y) :- node(X), node(Y), X < Y.

removed(X,Y,@delta(flip, (5,100), (X,Y))) :- edge(X,Y).

% {assign(X,C) : color(C)} = 1 :- node(X).
assign(X,red) :- node(X), not assign(X,green), not assign(X,blue).
assign(X,green) :- node(X), not assign(X,red), not assign(X,blue).
assign(X,blue) :- node(X), not assign(X,red), not assign(X,green).

:- edge(X,Y), not removed(X,Y,1), assign(X,C), assign(Y,C).

#show.
#show colorable.
