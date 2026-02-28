% 100 people in the lottery
person(1..200).

% Each person has a 1/1000 chance of winning
% This is a "Long Tail" event
winner(P, @delta(@mass(flip(1, 100000)), P)) :- person(P).

% The Goal: Exactly 3 people win out of 100
% This requires calculating the Binomial coefficient (100 choose 3)
% multiplied by the rare probabilities.
%target_met :- 3 = #count{P : winner(P, 1)}.

#show.
%#show target_met/0.
#show C : C = #count{P : winner(P, 1)}.