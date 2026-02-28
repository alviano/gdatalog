%*
Sequential System Degradation Model
The system survives through a sequence of time steps T.
At each step, health is sampled. If it drops to 0, the system fails.
Mission requirement: system must not fail before step 50.
*%

% Initial State: System starts at Step 0 with 100% Health
health(0, 100).

% The Health attrition is sampled at each step T.
attrition(T, @delta(randint(0, 5), T)) :- health(T, H), H > 0, T < 100.

% The next health level depends on the previous level and the random attrition.
health(T+1, H - A) :- health(T, H), attrition(T, A), H > A.
health(T+1, 0) :- health(T, H), attrition(T, A), H <= A.

% A 'failure' occurs if health drops to 0.
failed(T) :- health(T, 0).

% Mission Requirement: The system MUST NOT fail before step 50.
% Branches where the system fails early are discarded.
:- failed(T), T < 50.

#show.
#show health/2.
#show failed/1.

