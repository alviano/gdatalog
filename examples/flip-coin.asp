coin(1..3).

head(C, @delta(flip(1,3), C)) :- coin(C).

#show.
#show head(C) : head(C,1).
#show tail(C) : head(C,0).