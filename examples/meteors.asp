% https://towardsdatascience.com/the-poisson-distribution-and-poisson-process-explained-4e2cb17d459
%
% We were told to expect 5 meteors per hour on average.
% According to my pessimistic dad, that meant we'd see 3 meteors in an hour, tops.
% If we went outside every night for one week, then we could expect my dad to be right precisely once!

day(1..7).

meteors(D, @delta(poisson, (5,1), (D))) :- day(D).
dad_was_right_today(D) :- meteors(D,3).

#show.
#show dad_was_right(C) : C = #count{D : dad_was_right_today(D)}.


% Note that we group on the visible symbols. Eg. adding details is less informative:
% #show dad_was_right_today/1.
