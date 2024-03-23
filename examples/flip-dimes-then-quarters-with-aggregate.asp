% flip dimes...
% then flip quarters if an even number of dimes show head

dime(1..2).
quarter(5).

dime_head(C, @delta(flip(1,2), C)) :- dime(C).
even_dime_heads :- H = #count{C : dime_head(C,1)}, H \ 2 == 0.
quarter_head(C, @delta(flip(1,2), C)) :- quarter(C), even_dime_heads.

#show.
#show dime_head(C) : dime_head(C,1).
#show dime_tail(C) : dime_head(C,0).
#show quarter_head(C) : quarter_head(C,1).
#show quarter_tail(C) : quarter_head(C,0).
