% flip dimes...
% then flip quarters if no dime shows head

dime(a).
dime(b).

quarter(c).


dime_head(C, @delta(flip, (1,2), (C))) :- dime(C).
some_dime_head :- dime_head(C,1).
quarter_head(C, @delta(flip, (1,2), (C))) :- quarter(C), not some_dime_head.

#show.
#show dime_head(C) : dime_head(C,1).
#show dime_tail(C) : dime_head(C,0).
#show quarter_head(C) : quarter_head(C,1).
#show quarter_tail(C) : quarter_head(C,0).
