coin(1).

flip(C, @delta(((heads,1),(tails,2)), C)) :- coin(C).
coin(C+1) :- flip(C, heads).

#show.
#show flip/2.
