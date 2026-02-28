%*
In physics, a parent isotope decays into a daughter isotope, which might be unstable and decay again.
This continues until a stable state is reached.

In GDatalog, we can represent this as a sequence of events where each step's existence depends on the outcome of the previous one.
Specifically, in this model, we track a particle's state.
At each time step, there is a probability that it "decays" into a stable form or "persists" as an unstable one.
*%

% Start with an unstable isotope at time 0
particle(0, unstable).

% Determine if the unstable particle decays at step T
% The sequence is potentially infinite but terminates once 'stable' is reached.
particle(T+1,
    @delta((
        unstable(3),
        stable(1)
    ), T)) :- particle(T, unstable).

#show.
#show STEPS : particle(STEPS, stable).