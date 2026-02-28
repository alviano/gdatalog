% Start at level 1
level(1).
max_depth(10).

% At each level, discover N tunnels based on a Poisson(5)
% Poisson(5) means we expect 5, so seeing exactly 1 is rare (P ≈ 0.033)
tunnels(L, @delta(@mass(poisson(1,10)), L)) :- level(L), L <= 10.

% RECURSION: We only move to the next level if exactly 1 tunnel was found.
% This "biases" the search toward the low-outcome tail.
level(L+1) :- level(L), tunnels(L, 1), L < 10.

% SUCCESS: Reaching the bottom of the 10th level
reached_bottom :- level(11).

#show tunnels/2.
#show reached_bottom/0.