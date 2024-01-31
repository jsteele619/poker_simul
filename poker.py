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
            player = Player_instance('Player ' + str(x), 200)
            self.player_instances.append(player)

    def play_game(self):
        #Running functions to play game
        
        self.create_game_order()
        self.post_blinds()
        print("Dealing cards to players")
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
            if self.priority.has_bet and (self.priority.bet_this_round == self.player_priority_action):
                break

            if self.everyone_folded():
                print("winner")
                break

            elif self.priority.fold:
                self.priority = self.priority.next
                continue

            elif self.priority.all_in:
                self.priority.has_bet = True
                self.priority.bet_this_round = self.player_priority_action         # To break for loop, sloppy
                self.priority = self.priority.next
                continue

            else:
                bet_time = self.priority.game_action_player(self.player_priority_action)
                self.process_action(bet_time)

                print("Player Priority:", self.player_priority.name, "Priority:", self.priority.name, "Priority Action:", self.player_priority_action)
                self.priority = self.priority.next
        
        self.which_stage += 1 
        self.reset_priority()                

    def process_action(self, bet_time):
        if bet_time[0] == "raise":
            self.set_pot(bet_time[1])
            self.player_priority_action = self.priority.bet_this_round               # Needs work to finalize raise from called position
            self.player_priority = self.priority
            print(self.priority.name, "has raised", self.player_priority_action)

        if bet_time[0] == "call":
            print(self.priority.name, "has called")
            self.set_pot(bet_time[1])
        
        if bet_time[0] == "check":
            print(self.priority.name, "has checked")
            pass

        if bet_time[0] == "fold":
            print(self.priority.name, "has folded")
                
        if bet_time[0] == "all in":
            self.set_pot(bet_time[1])
            self.player_priority_action = self.priority.total_bet
            self.priority.bet_this_round = self.player_priority_action             # Sloppy
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
        print("posted blinds: sb:", self.small_blind.bet_this_round, "bb:", self.big_blind.bet_this_round, self.get_pot())

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
        print("Flop", self.print_cards(rand_card), self.print_cards(rand_card1), self.print_cards(rand_card2))

    def deal_turn(self):
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        print("Turn:", self.print_cards(rand_card))

    def deal_river(self):
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        print("River", self.print_cards(rand_card))

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
        if card[0] == 'clubs':
            return card[1], '\u2663'
        if card[0] == 'diamonds':
            return card[1], '\u2666'
        if card[0] == 'spades':
            return card[1], '\u2660'
        if card[0] == 'hearts':
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
                print(x.name, x.total_bet)

class Player_instance:
    def __init__(self, name, money):
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
        # Action refers to self.player_priority_action
        self.has_bet = True
        if self.all_in:
            return ["check", 0]
        
        elif action == self.bet_this_round:
            x = random.randint(2, 3)
            if x == 3:
                return ["check", 0]
            if x == 2:
                val = self.place_bet(10 + action)
                return ["raise", 10 + val]
        
        elif action > self.bet_this_round:
            x = random.randint(0, 3)
            if x == 0:
                self.all_in = True
                val = self.place_bet(self.money)
                return ["all in", val] 
            if x == 1: 
                val = self.place_bet(10 + action)
                return ["raise", val]
            if x == 2:
                val = self.place_bet(action) 
                return ["call", val]
            if x == 3:
                self.fold = True 
                return ["fold", 0]
        else:
            return["fold", 0]
        
    def place_bet(self, amount):                        # Place the bet with impact on player side, process bet on game state side
        # Reason to place bet
        if amount > self.money:
            val = amount % self.money
            self.money = 0
            self.all_in = True
            self.bet_this_round += val
            self.total_bet += val
            return val
        else:
            self.set_money(amount)
            self.bet_this_round += amount
            self.total_bet += amount
            return amount

    def get_money(self):
        return self.money

    def set_money(self, amount):            # Needs work
        self.money -= amount   

new_round = Game_instance(6, 2, 4)
new_round.create_game()
new_round.play_game()
