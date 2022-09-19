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

% {assign(X,C) : color(C)} = 1 :- node(X).
assign(X,red) :- node(X), not assign(X,green), not assign(X,blue).
assign(X,green) :- node(X), not assign(X,red), not assign(X,blue).
assign(X,blue) :- node(X), not assign(X,red), not assign(X,green).

:- edge(X,Y), not removed(X,Y,1), assign(X,C), assign(Y,C).

#show.
#show colorable.
