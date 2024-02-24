from deck import new_deck
from poker import Game_instance
import random

class AI_player(Game_instance):
    def __init__(self, name, money, game_instance):
        self.game_instance = game_instance
        self.name = name
        self.money = money
                                   
        self.next = None
        self.position = -1
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
            if {self.card1[1], self.card[2]} in hands:
                return rank

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

    def information_per_player(self):
        self.game_instance