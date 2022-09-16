city(gotham).
house(wayne_manor, gotham).
burglary_risk(gotham, (6,10)).

earthquake(C, @delta(flip, (1,10), (earthquake,C))) :- city(C).
burglary(H,C, @delta(flip, (N,D), (burglary,H,C))) :- house(H,C), burglary_risk(C,(N,D)).
trig(H,C, @delta(flip, (6,10), (trig_earthquake,H,C))) :- house(H,C), earthquake(C,1).
trig(H,C, @delta(flip, (9,10), (trig_burglary,H,C))) :- burglary(H,C,1).
alarm(H,C) :- trig(H,C,1).


#show.
#show earthquake(C) : earthquake(C,1).
#show burglary(H,C) : burglary(H,C,1).
#show alarm/2.