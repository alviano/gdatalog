coin(1).

head(C, @delta(flip, (1,3), (C))) :- coin(C).
coin(C+1) :- head(C,1).

#show.
#show head(C) : head(C,1).
#show tail(C) : head(C,0).
