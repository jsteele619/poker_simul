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

        # How Many Winners
        self.winner = [-1]
        self.multiple = []
        self.multiple_true = False
    
        # ACTIONS and MUTEABLES
        self.pot = 0
        self.player_priority_action = big                             # Most important action, aka highest bet
        self.player_priority = None                                    # Who did the action?
        self.priority = None                                            # Who's turn is it currently?
        self.num_players_in_round = num_players

    def create_game(self):
        # Create a player instance for each and append them to list of players
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
        print(self.print_cards(self.cards_public[0]), self.print_cards(self.cards_public[1]), self.print_cards(self.cards_public[2]), self.print_cards(self.cards_public[3]), self.print_cards(self.cards_public[4]))
        self.find_best_hand()
        self.print_pay_out()
        self.which_stage = 0
        
        self.reset_priority()
        self.reset_deck()

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
        # Needs work to rotate game order
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

    def reset_priority(self):
        self.priority = self.head.next
        self.player_priority = self.head
        self.player_priority_action = 0

        for player in self.player_instances:
            # Changing
            player.bet_this_round = 0
            player.has_bet = False

    def stage(self):
        if self.which_stage == 1:               # Ready to see the flop
            self.deal_flop()
        if self.which_stage == 2:
            self.deal_turn()
        if self.which_stage == 3:
            self.deal_river()
        

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
        num_folds = 0
        for player in self.player_instances:
            if player.fold == False:
                num_folds += 1
        return num_folds <= 1
        
    def everyone_all_in(self):
        y = 0
        for player in self.player_instances:
            if player.all_in == False:
                y += 1
        return y <= 1
        
    def get_pot(self):
        return self.pot

    def set_pot(self, amount):
        self.pot += amount

    def reset_pot(self):
        self.pot = 0

    def reset_deck(self):
        self.update_deck = new_deck[:]

    def payout_pot(self):
        pot = self.get_pot()
        if not self.multiple_true:
            player = self.winner[0]
            player.receive_payment(pot)
            
        if self.multiple_true:
            num_winners = len(self.winner)
            pot = self.get_pot()
            pot = pot // num_winners
            for winner in self.winner:
                winner.receive_payment(pot)
        
        self.reset_pot()

    def find_best_hand(self):
        ranks_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        # NEEDS WORK, sloppy
        for player in self.player_instances:
            if player.fold == True:
                continue
            else:
                # Return object is [2, ['Q', '9'], 'Two Pairs', ['10', '8', '2']], list of lists. 
                combo = Winning_hand.find_winning_hand([player.card1, player.card2, *self.cards_public])              # Returned object of analyzed hand
                
                if combo[0] > self.winner[0]:                                       
                    self.winner = [player, combo]
                elif combo[0] == self.winner[0]:                                    # If parts of the hand are equal
                    if combo[1][0] > self.winner[1][0]:
                        self.winner = [player, combo]
                    elif combo[1][0] == self.winner[1][0]:
                        if combo[1][1] > self.winner[1][1]:
                            self.winner = [player, combo]
                        elif combo[1][1] == self.winner[1][1]:
                            if (combo[3] == None) and (self.winner[3] == None):
                                self.multiple_true = True
                                self.multiple.append([player, combo])
                                break
                            self.multiple_true = True
                            self.multiple.append([player, combo])

    def print_pay_out(self):
        # Needs Work
        for player in self.player_instances:
            hand_analysis = Winning_hand.find_winning_hand([player.card1, player.card2, *self.cards_public])
            if not player.fold:
                if self.winner[0][0] == player:
                    print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, player.total_bet, "   Winner", hand_analysis)
                else:
                    print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, player.total_bet, hand_analysis)
            else:
                print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, player.total_bet, "     Folded:", hand_analysis)

class Player_instance(Game_instance):
    def __init__(self, name, money, game_instance):
        self.game_instance = game_instance
        self.name = name
        self.money = money
                                   
        self.next = None
        self.card1 = None
        self.card2 = None
        
        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

    def game_action_player(self, action):
        # Decide what to do, currently random game actions
        #print(self.pair_probability([self.card1, self.card2, *self.game_instance.cards_public]))
        #self.organize_ev_self([self.card1, self.card2, *self.game_instance.cards_public])
        print(self.print_cards(self.card1), self.print_cards(self.card2))
        #print(self.find_winning_hand())
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
            x = random.randint(2, 3)
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

    def range(self):
        starting_hands = {
            "10": []
        }
        
        pass

    def position(self):
        pass

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

    def receive_payout(self, amount):
        self.money += amount
        return self.money

class Winning_hand:
    @staticmethod
    def straight_flush(cards):
        return None 

    @staticmethod
    def flush(cards):
        # Check if any suit has 5 cards, indicating a flush
        suit_dict = {'h': 0, 'c': 0, 's': 0, 'd': 0}
        for card in cards:
            suit = card[0]
            suit_dict[suit] += 1

        flush_suit = None
        for suit, count in suit_dict.items():
            if count >= 5:
                flush_suit = suit
                break  # No need to check other suits if a flush is found

        if flush_suit:
            card_list = [card[1] for card in cards if card[0] == flush_suit]
            print(card_list)
            return [5, [card_list, 0], "Flush", card_list]  # Return the ranks of the cards forming the flush

        return None  # No flush found

    @staticmethod 
    def straight(cards):
        # Check for consecutive ones using a sliding window
        straight_bit_mask = 0b0000000000000
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        bitmask = 0b11111
        for i in range(9):
            window = straight_bit_mask >> i  # Shift the bits to create a window of 5 bits
            if window & bitmask == bitmask: # Found 5 consecutive ones
                left_rank_index = i  # Index of the leftmost bit in the sequence
                leftmost_rank = ranks[left_rank_index + 4]  # Rank corresponding to the leftmost bit
                return [4, [leftmost_rank, 0], "Straight", []]
    
    @staticmethod
    def find_winning_hand(cards):
        straight_bit_mask = 0b0000000000000
        pairs_dict = {'2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, 'J':0, 'Q':0, 'K':0, 'A':0 }
        suit_dict = {'h':0, 'c':0, 's':0, 'd':0}
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        for card in cards:
            suit_dict[card[0]] += 1                # Suit
            pairs_dict[card[1]] += 1               # Rank

            rank_index = ranks.index(card[1])
            bit_mask = 1 << rank_index
            straight_bit_mask |= bit_mask

        quad = []
        pairs = []
        triplets = []
        singles = []

        for key, val in pairs_dict.items():
            if val == 4:
                quad.append(key)
            elif val == 3:
                triplets.append(key)
            elif val == 2:
                pairs.append(key)
            elif val == 1:
                singles.append(key)

        #straight_flush_info = self.straight_flush()
        straight_info = Winning_hand.straight(cards)
        flush_info = Winning_hand.flush(cards)
        #print(singles[::-1])       # String of ['A', '8', '5', '4', '2']
        #if straight_flush_info is not None:
        #    return straight_flush_info
        if len(quad) == 1:  # One quad
            return [7, [quad[0], 0], "Quads", singles[::-1]]
        elif len(triplets) == 2:  # Two triplets mean Full House
            return [6, [max(triplets), min(triplets)], "Full House", []]
        elif len(triplets) == 1 and len(pairs) > 0:  # One triplet and some pairs make Full House
            return [6, [triplets[0], max(pairs)], "Full House", []]
        elif flush_info is not None:
            return flush_info
        elif straight_info is not None:
            return straight_info
        elif len(triplets) == 1:  # Only one triplet means Three of a Kind
            return [3, [triplets[0], 0], "Three of a Kind", singles[::-1]]
        elif len(pairs) == 2:  # Two pairs
            return [2, [max(pairs), min(pairs)], "Two Pairs", singles[::-1]]
        elif len(pairs) == 1:  # One pair
            return [1, [pairs[0], 0], "One Pair", singles[::-1]]
        else:
            highest_card = max(pairs_dict.keys())  # No special combination found, return High Card
            return [0, [highest_card, 0], "High Card", singles[::-1]]

class Probability:
    @staticmethod
    def flush_probability(cards):
        unseen_cards = 52 - len(cards)
        unseen_suits = {'h': 13, 'd': 13, 'c': 13, 's': 13}  
        
        for card in cards:
            suit = card[0] 
            unseen_suits[suit] -= 1  
        
        # Calculate the number of ways to get a flush
        flush_count = sum(1 for count in unseen_suits.values() if count >= 5)

        # Calculate the probability of getting a flush
        flush_probability = flush_count / unseen_cards
        return flush_probability
    
    @staticmethod
    def straight_probability(cards):          # TO DO
        pass
    
    @staticmethod
    def pair_probability(cards):
        unseen_cards = 52 - len(cards)
        unseen_pairs = 0

        for rank, count in self.pairs_dict.items():
            unseen_pairs += (4 - count) * (3 - count)  
            # Each unseen card could form a pair with each other unseen card of the same rank

        probability = unseen_pairs / unseen_cards * (unseen_pairs - 1) / (unseen_cards - 1)
        return probability

    @staticmethod
    def three_probability_given_pair(cards):
        unseen_cards = 52 - len(cards)
        probability = 2 / unseen_cards  # Probability of drawing one of the remaining two cards
        return probability
    
    @staticmethod
    def four_probability_given_three(cards):
        unseen_cards = 52 - len(cards)
        probability = 1 / unseen_cards
        return probability
    
    @staticmethod
    def full_house_probability(cards):
        pairs = []
        triplets = []
        for rank, count in self.pairs_dict.items():
            if count == 2:
                pairs.append(rank)
            elif count == 3:
                triplets.append(rank)

        if pairs and triplets:
            pair_prob = self.three_probability_given_pair(cards)
            three_prob = self.four_probability_given_three(cards)
            probability = pair_prob + three_prob
            return probability
        return 0  

for x in range(100):    
    new_round = Game_instance(8, 2, 4)
    new_round.create_game()
    new_round.play_game()
    print(x)



