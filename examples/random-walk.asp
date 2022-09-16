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

#show.
#show from/1.
#show to/1.
#show next(X,Y) : next(X,I), neighbor(X,I,Y).
