init( [ [ frank,   L1, O1, R1 ]
      , [ irene,   L2, O2, R2 ]
      , [ george,  L3, O3, R3 ]
      , [ heather, L4, O4, R4 ]
      , [ jerry,   L5, O5, R5 ]
      ] ) :-
    permutation([L1, L2, L3, L4, L5], [kirkwood, orange, north, maxwell, lake]),
    permutation([O1, O2, O3, O4, O5], [amplifier, candelabrum, banister, elephant, doorknob]),
    permutation([R1, R2, R3, R4, R5], [amplifier, candelabrum, banister, elephant, doorknob]).

hw(World) :-
    init(World),

    % The person who ordered the candelabrum received the banister.
    member([_, _, candelabrum, banister], World),

    % The customer who ordered banister received the package that Irene had ordered.
    member([irene, _, IrenesOrder, _], World),
    member([_, _, banister, IrenesOrder], World),

    % Frank received the doorknob.
    member([frank, _, _, doorknob], World),

    % George's package went to Kirkwood St.
    member([george, _, GeorgesPackage, _], World),
    member([_, kirkwood, _, GeorgesPackage], World),

    % The delivery that should have gone to Kirkwood Street was sent to Lake Avenue.
    member([_, kirkwood, KirkwoodDelivery, _], World),
    member([_, lake, _, KirkwoodDelivery], World),

    % Heather received the package that was to go to Orange Drive.
    member([heather, _, HeatherOrder, HeatherDelivery], World),
    member([_, orange, HeatherDelivery, _], World),

    % Jerry received Heather’s order.
    member([jerry, _, _, HeatherOrder], World),

    % The Elephant arrived in North Avenue.
    member([_, north, _, elephant], World),

    % The person who had ordered the elephant received the package that should
    % have gone to Maxwell Street.
    member([_, maxwell, MaxwellItem, _], World),
    member([_, _, elephant, MaxwellItem], World),

    % The customer on Maxwell Street received the Amplifier
    member([_, maxwell, _, amplifier], World).
