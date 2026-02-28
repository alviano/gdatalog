coin(1..3).

heads(C, @delta((2,1), C)) :- coin(C).

#show.
#show heads(C) : heads(C,1).
#show tails(C) : heads(C,0).