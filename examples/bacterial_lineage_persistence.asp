%*
Model the persistence of a bacterial lineage over generations, where each bacterium has a 50% chance of surviving to the next generation.
We want to determine the probability that the lineage persists for a certain number of generations.
*%

% Initial state: 100 bacteria at generation 0
population(0, 100).

% At each generation T, sample a survival count.
survival(T, @delta(@mass(binom(N, 1,2)), T)) :- population(T, N), N > 0.

% The next population is the number of survivors from the previous generation.
population(T+1, S) :- survival(T, S).

#show.
#show STEPS : population(STEPS, 0).
