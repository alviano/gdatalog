% 1. Initial Stock
stock(0, 10).

% 2. Incoming Shipment (Poisson)
% Every day, we receive a random batch of goods.
% Lambda = 5
incoming(T, @delta(@mass(poisson(5, 1)), (T))) :- T = 0..2.

% 3. Customer Orders (Binomial)
% Out of the current stock, there is a 30% chance each item is ordered.
% binom(N, 3, 10) represents B(n=N, p=0.3)
orders(T, @delta(@mass(binom(N, 3, 10)), (T))) :- stock(T, N), N > 0, T < 3.

% 4. There is a 1% chance of a warehouse audit that resets stock to 0.
audit(T+1, @delta((99, 1), T)) :- stock(T, N), T < 3.
stock(T, 0) :- audit(T, 1).

% 5. State Update
% Stock next day = Current + Incoming - Orders
stock(T+1, N + I - O) :- stock(T, N), audit(T+1, 0), incoming(T, I), orders(T, O), T < 3.

#show.
%#show incoming/2.
%#show orders/2.
%#show audit/2.
#show stock/2.