from deck import new_deck
import random

# POT
# Betting

# The betting round continues until all players have had the opportunity to act and all bets are matched. If there is only one player remaining after all others have folded, 
# that player wins the pot without the need for further action.

class Game_instance:
    def __init__(self, num_players, small, big):
        self.num_players = num_players
        self.player_instances = []
        self.deck = new_deck
        self.update_deck = new_deck
        
        self.big_blind_amount = big
        self.small_blind_amount = small
        self.head = None                                # Player
        self.small_blind = None                         # Player 
        self.big_blind = None                           # Player
        
        self.cards_public = []
        self.player_names = ['Alpha', 'Bravo', 'Chad', 'David', 'Eddie', 'Fred', 'George', 'Harry', 'Ian']
        self.stage_public = ['Pre', 'Flop', 'Turn', 'River', 'Show']
        self.which_stage = 0
    
        ## ACTIONS and MUTEABLES
        self.pot = 0
        self.player_priority_action = big                             # Most important action, aka highest bet
        self.player_priority = None                                    # Who did the action?
        self.priority = None                                            # Who's turn is it currently?
        self.num_players_in_round = num_players

    def create_game(self):
        # Create a player instance for each
        for x in range(self.num_players):
            player = Player_instance(self.player_names[x], 200, self)
            self.player_instances.append(player)

    def play_game(self):
        #Running functions to play game
        self.create_game_order()
        self.post_blinds()
        print("Dealing cards to players:\n ")
        self.deal_cards()
        self.game_action()
        self.stage()
        self.game_action()
        self.stage()
        self.game_action()
        self.stage()
        self.game_action()
        self.stage()
        #print(self.print_cards(self.cards_public[0]), self.print_cards(self.cards_public[1]), self.print_cards(self.cards_public[2]), self.print_cards(self.cards_public[3]), self.print_cards(self.cards_public[4]))
        self.print_pay_out()
        print(self.pot)
        self.which_stage = 0

    def game_action(self):
        while True:                                              # While the last acting player 
            if self.everyone_folded():
                break
            if self.priority.has_bet and (self.priority.bet_this_round == self.player_priority_action):
                break
            elif self.priority.fold:
                self.priority = self.priority.next
                continue
            elif self.priority.all_in:
                self.priority.has_bet = True
                self.priority = self.priority.next
                continue
            else:
                bet_time = self.priority.game_action_player(self.player_priority_action)
                self.process_action(bet_time)

                print("Active Player:", self.priority.name, "Player with Priority:", self.player_priority.name, "Priority Action:", self.player_priority_action, "\n")
                self.priority = self.priority.next
        
        self.which_stage += 1 
        self.reset_priority()                

    def process_action(self, bet_time):
        if bet_time[0] == "raise":
            self.set_pot(bet_time[1])
            self.player_priority_action = self.priority.bet_this_round               # Needs work to finalize raise from called position
            self.player_priority = self.priority
            print(self.priority.name, "has raised to", self.player_priority_action)

        if bet_time[0] == "call":
            print(self.priority.name, "has called")
            self.set_pot(bet_time[1])
        
        if bet_time[0] == "check":
            print(self.priority.name, "has checked")

        if bet_time[0] == "fold":
            print(self.priority.name, "has folded")
                
        if bet_time[0] == "all in":
            self.set_pot(bet_time[1])
            self.player_priority_action = self.priority.total_bet
            self.priority.bet_this_round = self.player_priority_action              # Sloppy
            print(self.priority.name, "is all-in")

    def create_game_order(self):
        # Game order created with linked list indicating positions "button", "small blind", and "big blind"
        self.head = self.player_instances[0]
        
        for i in range(0, self.num_players - 1):
            self.player_instances[i].next = self.player_instances[i+1]
            #print(self.player_instances[i].next.name)
    
        self.player_instances[-1].next = self.player_instances[0]
        self.small_blind = self.head.next
        self.big_blind = self.head.next.next
        self.priority = self.head.next.next.next
        self.player_priority = self.head.next.next    
        #print(self.player_instances[-1].next.name)
        #print(self.small_blind.name, self.big_blind.name)

    def post_blinds(self):
        # Correct setters to amount and pot
        self.small_blind.place_bet(self.small_blind_amount)
        self.set_pot(self.small_blind_amount)
        
        self.big_blind.place_bet(self.big_blind_amount)
        self.set_pot(self.big_blind_amount)
        #print("posted blinds: sb:", self.small_blind.bet_this_round, "bb:", self.big_blind.bet_this_round, self.get_pot())

    def deal_cards(self):
        for player in self.player_instances:
            ## Dealing two cards to each player, and deleting them from available cards
            rand_card = random.choice(self.update_deck)
            player.card1 = rand_card
            self.update_deck.remove(rand_card)

            rand_card = random.choice(self.update_deck)
            player.card2 = rand_card
            self.update_deck.remove(rand_card)

            #print(player.name + ': ', self.print_cards(player.card1), self.print_cards(player.card2))
    
    def deal_flop(self):
        # Deal Flop
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        rand_card1 = random.choice(self.update_deck)
        self.cards_public.append(rand_card1)
        self.update_deck.remove(rand_card1)
        rand_card2 = random.choice(self.update_deck)
        self.cards_public.append(rand_card2)
        self.update_deck.remove(rand_card2)
        print("\nFlop", self.print_cards(rand_card), self.print_cards(rand_card1), self.print_cards(rand_card2))

    def deal_turn(self):
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        print("\nTurn:", self.print_cards(rand_card))

    def deal_river(self):
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        print("\nRiver:", self.print_cards(rand_card))

    def reset_priority(self):
        self.priority = self.head.next
        self.player_priority = self.head
        self.player_priority_action = 0

        for x in self.player_instances:
            x.bet_this_round = 0
            x.has_bet = False

    def stage(self):
        if self.which_stage == 1:               # Ready to see the flop
            self.deal_flop()
        if self.which_stage == 2:
            self.deal_turn()
        if self.which_stage == 3:
            self.deal_river()
        
    def print_cards(self, card):
        if card[0] == 'c':
            return card[1], '\u2663'
        if card[0] == 'd':
            return card[1], '\u2666'
        if card[0] == 's':
            return card[1], '\u2660'
        if card[0] == 'h':
            return card[1], '\u2665'
    
    def everyone_folded(self):
        y = 0
        for x in self.player_instances:
            if x.fold == False:
                y += 1
        if y>1:
            return False
        else:
            return True
        
    def everyone_all_in(self):
        y = 0
        for x in self.player_instances:
            if x.all_in == False:
                y += 1
        if y>1:
            return False
        else:
            return True
        
    def get_pot(self):
        return self.pot

    def set_pot(self, amount):
        self.pot += amount

    def reset_pot(self):
        self.pot = 0

    def payout_pot(self, list):
        pass

    def print_pay_out(self):
        for x in self.player_instances:
            if x.fold == False:
                print(self.print_cards(x.card1), self.print_cards(x.card2), x.name, x.total_bet)
            else:
                print(self.print_cards(x.card1), self.print_cards(x.card2), x.name, x.total_bet, "     Folded:" ) 

class Player_instance(Game_instance):
    def __init__(self, name, money, game_instance):
        self.game_instance = game_instance
        self.name = name
        self.money = money
        self.next = None
        self.card1 = None
        self.card2 = None
        self.straight_bit_mask = 0b0000000000000
        self.pairs_dict = {'2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, 'J':0, 'Q':0, 'K':0, 'A':0 }
        self.suit_dict = {'h':0, 'c':0, 's':0, 'd':0}
        self.highest_rank_card = None

        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

    def game_action_player(self, action):
        # Decide what to do, currently random game actions
        print(self.pair_probability([self.card1, self.card2, *self.game_instance.cards_public]))
        self.has_bet = True
        if self.all_in:                                 # Shouldn't be necessary
            self.bet_this_round = action                 # To break the for loop, sloppy
            return ["check", 0]
        
        elif action == self.bet_this_round:             # If the action is equal to your action this round
            x = random.randint(2, 3)
            if x == 3:
                return ["check", 0]
            if x == 2:
                val = self.place_bet(20 + action)
                return ["raise", val]
            if x == 1 :                                  # Not Currently Accessible
                return ['all in', 10]
        
        elif action >= self.money:                      # If the raise is more than your current money
            x = random.randint(0, 1)
            if x == 0:                              
                val = self.place_bet(self.money)        # Call and All In
                return ['all in', val]                   
            else:
                self.fold = True
                return ['fold', 0] 
        
        elif action > self.bet_this_round:              # If the raise is more than you have bet this round
            x = random.randint(1, 3)
            if x == 0:                                  # Still strange
                self.all_in = True
                val = self.place_bet(self.money)
                return ["all in", val] 
            if x == 1: 
                val = self.place_bet(20 + action - self.bet_this_round)
                return ["raise", val]
            if x == 2:
                val = self.place_bet(action - self.bet_this_round) 
                return ["call", val]
            if x == 3:
                self.fold = True 
                return ["fold", 0]
        else:
            print('weird')
            return["fold", 0]
        
    def place_bet(self, amount):                        # Place the bet with impact on player side, process bet on game state side
        # Reason to place bet
        if amount > self.money:
            val = self.set_money(self.money)
            self.all_in = True
            return val
        val = self.set_money(amount)
        return val

    def get_money(self):
        return self.money

    def set_money(self, amount):            # Needs work
        self.money -= amount   
        self.bet_this_round += amount
        self.total_bet += amount
        return amount

    def organize_ev_self(self, cards):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for card in cards:
            self.suit_dict[card[0]] += 1                # Suit
            self.pairs_dict[card[1]] += 1               # Rank
            if highest_rank_card is None or ranks.index(card[1]) > ranks.index(highest_rank_card[1]):
                highest_rank_card = card

            rank_index = ranks.index(card[1])
            bit_mask = 1 << rank_index
            self.straight_bit_mask |= bit_mask

        print(self.straight_bit_mask)
    
    def find_best_hand(self, cards):
        pass

    def straight_or_flush(cards):
        pass

    def find_pairs_triplets_fulls_quads(cards):
        quad = []
        pairs = []
        triplets = []
        singles = []
        for key, val in cards.items():
            if val == 4:
                quad.append(int(key))
            elif val == 3:
                triplets.append(int(key))
            elif val == 2:
                pairs.append(int(key))
            elif val == 1:
                singles.append(key)
  
        if len(quad) == 1:  # One quad
            return [7, quad[0], None, "Quads", singles[::-1]]
        elif len(triplets) == 2:  # Two triplets mean Full House
            return [6, max(triplets), min(triplets), "Full House", None]
        elif len(triplets) == 1 and len(pairs) > 0:  # One triplet and some pairs make Full House
            return [6, triplets[0], max(pairs), "Full House", None]
        elif len(triplets) == 1:  # Only one triplet means Three of a Kind
            return [3, triplets[0], None, "Three of a Kind", singles[::-1]]
        elif len(pairs) == 2:  # Two pairs
            return [2, max(pairs), min(pairs), "Two Pairs", singles[::-1]]
        elif len(pairs) == 1:  # One pair
            return [1, pairs[0], None, "One Pair", singles[::-1]]
        else:
            highest_card = max(cards.keys())  # No special combination found, return High Card
            return [0, highest_card, None, "High Card", singles[::-1]]

    def pair_probability(self, cards):
        unseen_cards = 52 - len(cards)
        unseen_pairs = 0

        for rank, count in self.pairs_dict.items():
            unseen_pairs += (4 - count) * (3 - count)  
            # Each unseen card could form a pair with each other unseen card of the same rank

        probability = unseen_pairs / unseen_cards * (unseen_pairs - 1) / (unseen_cards - 1)
        return probability
    
new_round = Game_instance(8, 2, 4)
new_round.create_game()
new_round.play_game()
