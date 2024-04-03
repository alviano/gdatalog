% sample space {0,1}; P(0) = 1/3, P(1) = 2/3
flip_with_index(@delta((1,2))).

% sample space {heads, tails}; P(heads) = 1/3, P(tails) = 2/3
flip_with_pairs(@delta((
    (heads,1),
    (tails,2)
))).

% sample space {heads, tails}; P(heads) = 1/3, P(tails) = 2/3
flip_with_names(@delta((
    heads(1),
    tails(2)
))).

% sample space {heads, tails}; P(heads) = 1/3, P(tails) = 2/3
flip_with_pairs_and_names(@delta((
    heads(1),
    (tails, 2)
))).
