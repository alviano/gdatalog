connection(a,b).
connection(a,c).
connection(b,c).
connection(Y,X) :- connection(X,Y).

router(X) :- connection(X,_).

infected(a,1).


infected(Y,@delta(flip, (10,100), (X,Y))) :- infected(X,1), connection(X,Y).
healthy(X) :- router(X), not infected(X,1).
:- healthy(X), healthy(Y), connection(X,Y).

#show.
#show infected(X) : infected(X,1).
