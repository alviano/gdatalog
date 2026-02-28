holes(10).
waves(5).

hole(1..H) :- holes(H).

fail_0 :- #false.
pigeon_0(0) :- #false.
wave_0(0).
hole_0(H) :- hole(H).


hole_1(H-N) :- hole_0(H), not pigeon_0(H), wave_0(N).

wave_1(@delta(@mass(poisson(2*C+1,1, 1000000, 900000)), 1)) :- C = #count{H : hole_1(H)}, not fail_0.

pigeon_1(1..N) :- wave_1(N).
fail_1 :- pigeon_1(P), not hole_1(P).





hole_2(H-N) :- hole_1(H), not pigeon_1(H), wave_1(N).

wave_2(@delta(@mass(poisson(2*C+1,1, 1000000, 900000)), 2)) :- C = #count{H : hole_2(H)}, not fail_1.

pigeon_2(1..N) :- wave_2(N).
fail_2 :- pigeon_2(P), not hole_2(P).





hole_3(H-N) :- hole_2(H), not pigeon_2(H), wave_2(N).

wave_3(@delta(@mass(poisson(2*C+1,1, 1000000, 900000)), 3)) :- C = #count{H : hole_3(H)}, not fail_2.

pigeon_3(1..N) :- wave_3(N).
fail_3 :- pigeon_3(P), not hole_3(P).





hole_4(H-N) :- hole_3(H), not pigeon_3(H), wave_3(N).

wave_4(@delta(@mass(poisson(2*C+1,1, 1000000, 900000)), 4)) :- C = #count{H : hole_4(H)}, not fail_3.

pigeon_4(1..N) :- wave_4(N).
fail_4 :- pigeon_4(P), not hole_4(P).





hole_5(H-N) :- hole_4(H), not pigeon_4(H), wave_4(N).

wave_5(@delta(@mass(poisson(2*C+1,1, 1000000, 900000)), 5)) :- C = #count{H : hole_5(H)}, not fail_4.

pigeon_5(1..N) :- wave_5(N).
fail_5 :- pigeon_5(P), not hole_5(P).





% Success: We survived both waves
#show.
#show survived : not fail_1, not fail_2, not fail_3, not fail_4, not fail_5.
