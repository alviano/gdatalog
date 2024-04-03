coin(1).

heads(C, @delta((1,2), C)) :- coin(C).
coin(C+1) :- heads(C, 1).

#show.
#show heads(C) : heads(C,1).
#show tails(C) : heads(C,0).
