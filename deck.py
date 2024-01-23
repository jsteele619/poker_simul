suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

new_deck = []
for suit in suits:
    for rank in ranks:
        new_deck.append([suit, rank])

