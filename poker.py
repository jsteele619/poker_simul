from deck import new_deck
import random
import pandas as pd

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
        self.player_names = ['Alpha', 'Bravo', 'Chad', 'David', 'Eddie', 'Fred', 'George']
        self.stage_public = ['Pre', 'Flop', 'Turn', 'River', 'Show']
        self.which_stage = 0
    
        # ACTIONS and MUTEABLES
        self.pot = 0
        self.player_priority_action = big                             # Most important action, aka highest bet
        self.player_priority = None                                    # Who did the action?
        self.priority = None                                            # Who's turn is it currently?
        self.num_players_in_round = num_players

    def create_game(self):
        # Create a player instance for each and append them to list of players
        for x in range(self.num_players - 1):
            player = Player_instance(self.player_names[x], 200, self)                   
            self.player_instances.append(player)
        ai_player = AI_player("Hero", 200, self)
        self.player_instances.append(ai_player)
        
    def play_game(self):
        #Running functions to play game
        self.post_blinds()
        print("Dealing cards to players:\n",)
        self.deal_cards()
        self.game_action()
        self.deal_flop()
        self.game_action()
        self.deal_turn()
        self.game_action()
        self.deal_river()
        self.game_action()
        print("\n", "Public Cards:", "\n", self.print_cards(self.cards_public[0]), self.print_cards(self.cards_public[1]), self.print_cards(self.cards_public[2]), self.print_cards(self.cards_public[3]), self.print_cards(self.cards_public[4]))
        self.end_of_game_action()

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
                self.priority = self.priority.next
                continue
            else:
                bet_time = self.priority.game_action_player(self.player_priority_action)
                self.process_action(bet_time)

               # print("Active Player:", self.priority.name, "Player with Priority:", self.player_priority.name, "Priority Action:", self.player_priority_action, "\n")
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
            self.player_priority_action = self.priority.total_bet                   # Incorrect ?
            self.priority.bet_this_round = self.player_priority_action              # Sloppy
            print(self.priority.name, "is all-in")

    def end_of_game_action(self):
        self.find_best_hand()
        self.print_pay_out()
        # Create AI adjustments

        self.payout_pot()
        self.reset_deck()
        for player in self.player_instances:
            player.reset_player()
        self.rotate_game_order()
        self.define_position()
        self.which_stage = 0

    def create_game_order(self):
        # Game order created with linked list indicating positions "button", "small blind", and "big blind"
        self.head = self.player_instances[0]
        
        for i in range(0, self.num_players - 1):
            self.player_instances[i].next = self.player_instances[i+1]
    
        self.player_instances[-1].next = self.player_instances[0]
        self.small_blind = self.head.next
        self.big_blind = self.head.next.next
        self.priority = self.head.next.next.next
        self.player_priority = self.head.next.next    

    def reset_priority(self):
        self.priority = self.head.next
        self.player_priority = self.head
        self.player_priority_action = 0

        for player in self.player_instances:
            player.bet_this_round = 0
            player.has_bet = False

    def rotate_game_order(self):
        self.head = self.head.next
        self.small_blind = self.head.next
        self.big_blind = self.head.next.next
        self.priority = self.head.next.next.next
        self.player_priority = self.head.next.next  
        self.player_priority_action =self.big_blind_amount 
        
    def define_position(self):
        self.small_blind.position = 0
        self.big_blind.position = 1
        variable = self.big_blind.next
        self.num_players_in_round = self.num_players
        x = 2
        
        while variable != self.small_blind:
            variable.position = x
            x += 1
            variable = variable.next

    def update_positions(self):
        x = 0
        variable = self.small_blind.next
        while variable != self.small_blind:
            if variable.fold:
                variable = variable.next
                continue
            else: 
                variable.position = x
                x += 1
                variable = variable.next
        self.num_players_in_round = x

    def post_blinds(self):
        # Correct setters to amount and pot
        self.small_blind.place_bet(self.small_blind_amount)
        self.set_pot(self.small_blind_amount)
        
        self.big_blind.place_bet(self.big_blind_amount)
        self.set_pot(self.big_blind_amount)
        print("Posted blinds: Small:", self.small_blind.name, self.small_blind.bet_this_round, "Big:", self.big_blind.name, self.big_blind.bet_this_round, self.get_pot())

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
        self.cards_public = []

    def payout_pot(self):
        pot = self.get_pot()
        print("Name of Winner:", self.winner[0].name, " Amount:", pot)
        print("\n")
        num_winners = len(self.winner)
        pot = pot // num_winners

        for winner in self.winner:
            winner.receive_payout(pot)
             
        self.reset_pot()

    def find_best_hand(self):
        ranks_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2, '1': 1, '0': 0}
        
        self.winner = []
        self.winning_hand = [0, ['0', '0'], 'High Card', ['0', '0', '0', '0', '0']]

        for player in self.player_instances:
            if player.fold == True:
                continue
            else:
                # Return object is [2, ['Q', '9'], 'Two Pairs', ['10', '8', '2']], list of lists. 
                combo = Winning_hand.find_winning_hand([player.card1, player.card2, *self.cards_public])              # Returned object of analyzed hand
                if combo[0] < self.winning_hand[0]:
                    continue
                elif combo[0] > self.winning_hand[0]:
                    self.winner = []
                    self.winner.append(player)
                    self.winning_hand = combo
                    continue
                elif combo[0] == self.winning_hand[0]:
                    if ranks_order[combo[1][0]] < ranks_order[self.winning_hand[1][0]]:
                        continue
                    elif ranks_order[combo[1][0]] > ranks_order[self.winning_hand[1][0]]:
                        self.winner = []
                        self.winner.append(player)
                        self.winning_hand = combo
                        continue
                    elif ranks_order[combo[1][0]] == ranks_order[self.winning_hand[1][0]]:
                        if ranks_order[combo[1][1]] < ranks_order[self.winning_hand[1][1]]:
                            continue
                        elif ranks_order[combo[1][1]] > ranks_order[self.winning_hand[1][1]]:
                            self.winner = []
                            self.winner.append(player)
                            self.winning_hand = combo
                            continue
                        elif ranks_order[combo[1][1]] == ranks_order[self.winning_hand[1][1]]:
                            if ranks_order[combo[1][0]] < ranks_order[self.winning_hand[1][0]]:
                                continue
                            elif ranks_order[str(combo[3][0])] > ranks_order[str(self.winning_hand[3][0])]:
                                self.winner = []
                                self.winner.append(player)
                                self.winning_hand = combo
                                continue
                            elif ranks_order[str(combo[3][0])] == ranks_order[str(self.winning_hand[3][0])]:
                                self.winner.append(player)
                else:
                    print("lord help me")
                    continue
                      
    def print_pay_out(self):
        for player in self.player_instances:
            combo = Winning_hand.find_winning_hand([player.card1, player.card2, *self.cards_public])
            if player in self.winner:
                print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, player.total_bet, "   Winner", combo)
            elif player.fold:
                print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, "   Folded", player.total_bet, combo)
            else:
                print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, "   Lost Showdown", player.total_bet, combo)
        #else:
        #    print(self.print_cards(player.card1), self.print_cards(player.card2), player.name, player.total_bet, "     Folded:", combo)

    def create_pandas_df(self):
        player_data = []
        for player in self.player_instances:
            player_info = {'Name': player.name}
            player_data.append(player_info)
            
        df = pd.DataFrame(player_data).set_index('Name').T
        return df
    
    def print_csv(self):
        player_list = []
        for player in self.player_instances:
            #print(player.name, ": ", player.money - (200 * player.buyins))
            player_list.append(player.money - (200 * player.buyins))
        return player_list
        

class AI_player(Game_instance):
    def __init__(self, name, money, game_instance):
        self.game_instance = game_instance
        self.name = name
        self.money = money
        self.buyins = 1
                                   
        self.next = None
        self.position = -1
        self.card1 = None
        self.card2 = None
        
        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

        self.position_weight = 1
        self.hand_strength = 1
        self.probability_strength = 1
        self.range_weight = 1
        self.combo_weight = 1
        self.action_weight = 1
        self.pot_odds_weight = 1
        self.random_val = .05

        self.preflop_val_one = 5
        self.preflop_val_two = 3
        self.preflop_val_three = 1

        self.postflop_val_one = 5
        self.postflop_val_two = 3
        self.postflop_val_three = 1


    def game_action_player(self, action):
        # Decide what to do
        print("\n", self.print_cards(self.card1), self.print_cards(self.card2))
        
        if self.game_instance.which_stage == 0:
            return self.preflop_bet(action)
        else:
            return self.postflop_bet(action)
        
    def preflop_bet(self, action):
        range_val = self.range()
        position_index = self.position_index()

        what_to_do = (int(range_val) * self.range_weight) + (position_index * self.position_weight) / 2
        print("What it do", what_to_do, "Range Val:", range_val, "Position Val:", position_index)
        self.has_bet = True
        if what_to_do > self.preflop_val_one:
            val = self.place_bet(4 * self.game_instance.big_blind_amount)
            return ["raise", val]
        elif what_to_do > self.preflop_val_two:
            action = self.place_bet(action)
            return ["call", action]
        else:
            self.fold = True
            self.game_instance.update_positions()
            return ['fold', 0]
    
    def postflop_bet(self, action):
        pot_odds_val = self.pot_odds(action)
        combo = Winning_hand.find_winning_hand([self.card1, self.card2, *self.game_instance.cards_public])
        position = self.position_index()
        range_val = self.range()
        self.has_bet = True

        what_to_do = (combo[0] * self.hand_strength) * (position * self.position_weight) * (pot_odds_val * self.pot_odds_weight) * (int(range_val)/10 * self.range_weight)
        print(what_to_do)

        if self.all_in:
            return ["all-in", 0]

        if action == self.bet_this_round:       # Checked to you    
            if what_to_do > 2:
                val = self.place_bet(self.game_instance.get_pot() * .7 * random.uniform(0.7, 1.3))      # Strong hand bet * .7 of pot * random
                if self.all_in:
                    return ["all in", val] 
                return ["raise", val]
            elif what_to_do > 1:
                val = self.place_bet(self.game_instance.get_pot() * .4 * random.uniform(0.7, 1.1))      # Medium hand bet * .4 of pot * random
                if self.all_in:
                    return ["all in", val] 
                return ["raise, val"]
            elif what_to_do < 1:
                return ["check", 0]
        
        elif action > self.bet_this_round:
            if what_to_do > 2:
                val = self.place_bet(self.game_instance.get_pot() * .7 * random.uniform(0.7, 1.3))
                if self.all_in:
                    return ["all in", val]      
                return ["raise", val]
            elif what_to_do > 1:
                val = self.place_bet(action)  
                if self.all_in:
                    return ["all in", val]    
                return ["call", val]
            elif what_to_do < 1:
                self.fold = True
                return ["fold", 0]

    def range(self):
        starting_hands = {
            "10": [{"A", "A"}, {"A", "K"}, {"K", "K"}, {"Q", "Q"}],
            "9": [{"A", "Q"}, {"A", "J"}, {"K", "J"}, {"K", "Q"}, {"Q", "J"}, {"J", "J"}],
            "8": [{"A", "10"}, {"K", "10"}, {"Q", "10"}, {"10", "10"}, {"9", "9"}],
            "7": [{"A", "9"}, {"K", "9"}, {"J", "10"}, {"Q", "9"}, {"10", "9"}, {"8", "8"}, {"7", "7"}],
            "6": [{"A", "8"}, {"A", "7"}, {"K", "8"}, {"Q", "9"}, {"Q", "8"}, {"J", "9"}, {"J", "8"}, {"10", "8"}, {"9", "8"}],
            "5": [{"A", "6"}, {"A", "5"}, {"K", "7"}, {"K", "6"}, {"Q", "7"}, {"J", "7"}, {"6", "6"}, {"5", "5"},],   
            "4": [{"A", "4"}, {"A", "3"}, {"A", "2"}, {"K", "5"}, {"K", "4"}, {"K", "3"}, {"K", "2"}, {"Q", "6"}, {"J", "6"}, 
                  {"10", "7"}, {"10", "6"}, {"9", "7"}, {"9", "6"}, {"8", "7"}, {"8", "6"}, {"7", "6"}, {"6", "5"}, {"4", "4"}, {"3", "3"}, {"2", "2"}],
            "2": [{"Q", "5"}, {"Q", "4"}, {"Q", "3"}, {"Q", "2"}, {"J", "5"}, {"J", "4"}, {"J", "3"}, {"J", "2"}, {"10", "5"}, 
                  {"10", "4"}, {"9", "5"}, {"8", "5"}, {"3", "2"}],
            "0": [{"10", "3"}, {"10", "2"}, {"9", "4"}, {"9", "3"}, {"9", "2"}, {"8", "4"}, {"8", "3"}, {"8", "2"}, {"7", "5"},  {"7", "4"}, 
                  {"7", "3"}, {"7", "2"}, {"6", "5"}, {"6", "3"}, {"6", "4"}, {"4", "2"}, {"5", "4"}, {"5", "3"}, {"6", "2"}, {"5", "2"}, {"3", "2"}, {"4", "3"}], 
        }

        for rank, hands in starting_hands.items():
            if {self.card1[1], self.card2[1]} in hands:
                return rank

    def pot_odds23(self, action, cards):
        pot = self.game_instance.get_pot()
        flush_prob = Probability.flush_probability(cards)
        pair_prob = Probability.two_pair_probability(cards)
        triplet_prob = Probability.three_probability_given_pair(cards)
        quad = Probability.four_probability_given_three(cards)
        full_house = Probability.full_house_probability(cards)

        #print(flush_prob, pair_prob, triplet_prob, quad, full_house)

    def position_index(self):
        # print("position", self.position, "num_player", self.game_instance.num_players_in_round)
        return (self.position/self.game_instance.num_players_in_round) * 10

    def pot_odds(self, action):
        # Pot size if bet called
        percentage = (action / self.game_instance.get_pot() + action)
        print("Pot Odds: ", percentage)
        return percentage

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

    def set_money(self, amount):           
        self.money -= amount   
        self.bet_this_round += amount
        self.total_bet += amount
        return amount

    def receive_payout(self, amount):
        self.money += amount
        return self.money

    def reset_player(self):
        if self.money == 0:
            self.money = 200
            self.buyins += 1
        
        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

    def create_information_per_player(self):
        player_info = []
        for player in self.game_instance.player_instances:
            if player != self:
                player_info.append({player.name: [{"VPIP": 0, "Preflop Raises": 0}]})

    def information_per_player(self):
        # Preflop Raises - e PFR statistic indicates how often you have raised before the flop is seen. A high value is an indicator of an aggressive player. 
        # A low value indicates a passive player. Good players are aggressive players.
        
        #Voluntarily Put $ in Pot (VPIP)
        #VPIP in poker measures how often you voluntarily pay money into a hand before seeing the flop. 
        
        # Postflop Aggression Frequency
        # Big Blinds won/ 100 Hands


        pass
    
    def ai_info_self(self):
        pass

class Player_instance(Game_instance):
    def __init__(self, name, money, game_instance):
        self.game_instance = game_instance
        self.name = name
        self.money = money
        self.buyins = 1
                                   
        self.next = None
        self.position = -1
        self.card1 = None
        self.card2 = None
        
        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

        self.position_weight = 1
        self.hand_strength = 1
        self.probability_strength = 1
        self.range_weight = 1
        self.combo_weight = 1
        self.action_weight = 1
        self.pot_odds_weight = 1
        self.random_val = .05

    def game_action_player(self, action):
        # Decide what to do
        print(self.print_cards(self.card1), self.print_cards(self.card2))
        
        if self.game_instance.which_stage == 0:
            return self.preflop_bet(action)
        else:
            return self.postflop_bet(action)
        
    def pot_odds(self, action):
        # Pot size if bet called
        percentage = (action / self.game_instance.get_pot() + action)
        return percentage

    def preflop_bet(self, action):
        range_val = self.range()
        position_index = self.position_index()
        pot_odds_val = self.pot_odds(action)

        what_to_do = (int(range_val)/9 * self.range_weight) * (self.position_index() * self.position_weight)
        self.has_bet = True
        if what_to_do > .5:
            val = self.place_bet(4 * self.game_instance.big_blind_amount)
            return ["raise", val]
        elif what_to_do > .3:
            action = self.place_bet(action)
            return ["call", action]
        else:
            self.fold = True
            self.game_instance.update_positions()
            return ['fold', 0]
    
    def postflop_bet(self, action):
        pot_odds_val = self.pot_odds(action)
        combo = Winning_hand.find_winning_hand([self.card1, self.card2, *self.game_instance.cards_public])
        position = self.position_index()
        range_val = self.range()
        self.has_bet = True

        what_to_do = (combo[0] * self.hand_strength) * (position * self.position_weight) * (pot_odds_val * self.pot_odds_weight) * (int(range_val)/10 * self.range_weight)

        if self.all_in:
            return ["all-in", 0]

        if action == self.bet_this_round:       # Checked to you    
            if what_to_do > 2:
                val = self.place_bet(self.game_instance.get_pot() * .7 * random.uniform(0.7, 1.3))      # Strong hand bet * .7 of pot * random
                if self.all_in:
                    return ["all in", val] 
                return ["raise", val]
            elif what_to_do > 1:
                val = self.place_bet(self.game_instance.get_pot() * .4 * random.uniform(0.7, 1.1))      # Medium hand bet * .4 of pot * random
                if self.all_in:
                    return ["all in", val] 
                return ["raise, val"]
            elif what_to_do < 1:
                return ["check", 0]
        
        elif action > self.bet_this_round:
            if what_to_do > 2:
                val = self.place_bet(self.game_instance.get_pot() * .7 * random.uniform(0.7, 1.3))
                if self.all_in:
                    return ["all in", val]      
                return ["raise", val]
            elif what_to_do > 1:
                val = self.place_bet(action)  
                if self.all_in:
                    return ["all in", val]    
                return ["call", val]
            elif what_to_do < 1:
                self.fold = True
                return ["fold", 0]


    def range(self):
        starting_hands = {
            "10": [{"A", "A"}, {"A", "K"}, {"K", "K"}, {"Q", "Q"}],
            "9": [{"A", "Q"}, {"A", "J"}, {"K", "J"}, {"K", "Q"}, {"Q", "J"}, {"J", "J"}],
            "8": [{"A", "10"}, {"K", "10"}, {"Q", "10"}, {"10", "10"}, {"9", "9"}],
            "7": [{"A", "9"}, {"K", "9"}, {"J", "10"}, {"Q", "9"}, {"10", "9"}, {"8", "8"}, {"7", "7"}],
            "6": [{"A", "8"}, {"A", "7"}, {"K", "8"}, {"Q", "9"}, {"Q", "8"}, {"J", "9"}, {"J", "8"}, {"10", "8"}, {"9", "8"}],
            "5": [{"A", "6"}, {"A", "5"}, {"K", "7"}, {"K", "6"}, {"Q", "7"}, {"J", "7"}, {"6", "6"}, {"5", "5"},],   
            "4": [{"A", "4"}, {"A", "3"}, {"A", "2"}, {"K", "5"}, {"K", "4"}, {"K", "3"}, {"K", "2"}, {"Q", "6"}, {"J", "6"}, 
                  {"10", "7"}, {"10", "6"}, {"9", "7"}, {"9", "6"}, {"8", "7"}, {"8", "6"}, {"7", "6"}, {"6", "5"}, {"4", "4"}, {"3", "3"}, {"2", "2"}],
            "2": [{"Q", "5"}, {"Q", "4"}, {"Q", "3"}, {"Q", "2"}, {"J", "5"}, {"J", "4"}, {"J", "3"}, {"J", "2"}, {"10", "5"}, 
                  {"10", "4"}, {"9", "5"}, {"8", "5"}, {"3", "2"}],
            "0": [{"10", "3"}, {"10", "2"}, {"9", "4"}, {"9", "3"}, {"9", "2"}, {"8", "4"}, {"8", "3"}, {"8", "2"}, {"7", "5"},  {"7", "4"}, 
                  {"7", "3"}, {"7", "2"}, {"6", "5"}, {"6", "3"}, {"6", "4"}, {"4", "2"}, {"5", "4"}, {"5", "3"}, {"6", "2"}, {"5", "2"}, {"3", "2"}, {"4", "3"}], 
        }

        for rank, hands in starting_hands.items():
            if {self.card1[1], self.card2[1]} in hands:
                return rank

    def pot_odds23(self, action, cards):
        pot = self.game_instance.get_pot()
        flush_prob = Probability.flush_probability(cards)
        pair_prob = Probability.two_pair_probability(cards)
        triplet_prob = Probability.three_probability_given_pair(cards)
        quad = Probability.four_probability_given_three(cards)
        full_house = Probability.full_house_probability(cards)

        #print(flush_prob, pair_prob, triplet_prob, quad, full_house)

    def position_index(self):
        return self.position/self.game_instance.num_players_in_round

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

    def set_money(self, amount):           
        self.money -= amount   
        self.bet_this_round += amount
        self.total_bet += amount
        return amount

    def receive_payout(self, amount):
        self.money += amount
        return self.money

    def reset_player(self):
        if self.money == 0:
            self.money = 200
            self.buyins += 1
        
        self.bet_this_round = 0
        self.total_bet = 0
        self.has_bet = False
        
        self.all_in = False
        self.fold = False

class Winning_hand:
    @staticmethod
    def straight_flush(cards):
        return None 

    @staticmethod
    def flush(cards):
        # Check if any suit has 5 cards, indicating a flush
        card_list = []
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
        count_dict = {'2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, 'J':0, 'Q':0, 'K':0, 'A':0 }
        suit_dict = {'h':0, 'c':0, 's':0, 'd':0}
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        for card in cards:
            suit_dict[card[0]] += 1                # Suit
            count_dict[card[1]] += 1               # Rank

            rank_index = ranks.index(card[1])
            bit_mask = 1 << rank_index
            straight_bit_mask |= bit_mask

        quad = []
        pairs = []
        triplets = []
        singles = []

        for key, val in count_dict.items():
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
        #flush_info = Winning_hand.flush(cards)
        #print(singles[::-1])       # String of ['A', '8', '5', '4', '2']
        #if straight_flush_info is not None:
        #    return straight_flush_info
        if len(quad) == 1:  # One quad
            return [7, [str(quad[0]), '0'], "Quads", singles[::-1]]
        elif len(triplets) == 2:  # Two triplets mean Full House
            return [6, [str(max(triplets)), str(min(triplets))], "Full House", [0,0,0]]
        elif len(triplets) == 1 and len(pairs) > 0:  # One triplet and some pairs make Full House
            return [6, [str(triplets[0]), str(max(pairs))], "Full House", [0,0,0]]
        #elif flush_info is not None:
        #    return flush_info
        elif straight_info is not None:
            return straight_info
        elif len(triplets) == 1:  # Only one triplet means Three of a Kind
            return [3, [str(triplets[0]), '1'], "Three of a Kind", singles[::-1]]
        elif len(pairs) == 2:  # Two pairs
            return [2, [str(max(pairs)), str(min(pairs))], "Two Pairs", singles[::-1]]
        elif len(pairs) == 1:  # One pair
            return [1, [str(pairs[0]), '1'], "One Pair", singles[::-1]]
        else:
            highest_card = str(max(count_dict.keys()))  # No special combination found, return High Card
            return [0, [str(highest_card), '1'], "High Card", singles[::-1]]

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
    # TO DO
    def straight_probability(cards):          
        pass
    
    @staticmethod
    def two_pair_probability(cards):
        count_dict = {'2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, 'J':0, 'Q':0, 'K':0, 'A':0 }
        unseen_cards = 52 - len(cards)
        unseen_pairs = 0

        for card in cards:
            rank = card[1]  # Assuming card is represented as a tuple (suit, rank)
            count_dict[rank] += 1

        for count in count_dict.values():
            unseen_pairs += (4 - count) * (count)  # Update calculation based on actual counts

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
        count_dict = {'2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0, 'J':0, 'Q':0, 'K':0, 'A':0 }
        pairs = []
        triplets = []

        for card in cards:
            count_dict[card[1]] += 1

        for rank, count in count_dict.items():
            if count == 2:
                pairs.append(rank)
            elif count == 3:
                triplets.append(rank)

        if pairs and triplets:
            pair_prob = Probability.three_probability_given_pair(cards)
            three_prob = Probability.four_probability_given_three(cards)
            probability = pair_prob + three_prob
            return probability
        return 0  

