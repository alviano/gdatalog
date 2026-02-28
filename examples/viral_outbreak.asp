% 1. Initial State
intensity(0, 3).

% 2. The Step: Lambda is half of N (N/2).
% We use (N, 2) to represent the fraction 1/2.
intensity(T+1, @delta(@mass(poisson(N, 2)), (T))) :- intensity(T, N), N > 0, T < 4.

:- not intensity(_, 0).

% 3. Output
#show.
#show STEPS : intensity(STEPS, 0).