from deck import new_deck
import random

# POT
# Betting

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
        self.priority = 0                                            # Who's turn is it currently?

    def create_game(self):
        # Create a player instance for each
        for x in range(self.num_players):
            player = Player_instance('Player ' + str(x), 100)
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
        print(self.print_cards(self.cards_public[0]), self.print_cards(self.cards_public[1]), self.print_cards(self.cards_public[2]), self.print_cards(self.cards_public[3]), self.print_cards(self.cards_public[4]))

    def create_game_order(self):
        # Game order created with linked list indicating positions "button", "small blind", and "big blind"
        self.head = self.player_instances[0]
        
        for i in range(0, self.num_players - 1):
            self.player_instances[i].next = self.player_instances[i+1]
            #print(self.player_instances[i].next.name)
    
        self.player_instances[-1].next = self.player_instances[0]
        self.small_blind = self.head.next
        self.big_blind = self.head.next.next
        self.prior = self.head.next.next
        self.priority = self.head.next.next.next
                       
        #print(self.player_instances[-1].next.name)
        #print(self.small_blind.name, self.big_blind.name)

    def post_blinds(self):
        # Correct setters to amount and pot
        pot_blind = self.small_blind.place_bet(self.small_blind_amount)
        self.set_pot(pot_blind)
        pot_blind = self.big_blind.place_bet(self.big_blind_amount)
        self.set_pot(pot_blind)
       
    def deal_cards(self):
        for player in self.player_instances:
            ## Dealing two cards to each player, and deleting them from available cards
            rand_card = random.choice(self.update_deck)
            player.card1 = rand_card
            self.update_deck.remove(rand_card)

            rand_card = random.choice(self.update_deck)
            player.card2 = rand_card
            self.update_deck.remove(rand_card)

            print(player.name + ': ', self.print_cards(player.card1), self.print_cards(player.card2))
        print("")
    
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
        print(self.print_cards(rand_card), self.print_cards(rand_card1), self.print_cards(rand_card2))

    def deal_one_card(self):
        rand_card = random.choice(self.update_deck)
        self.cards_public.append(rand_card)
        self.update_deck.remove(rand_card)
        print(self.print_cards(rand_card))

    def game_action(self):
        while self.priority != self.player_priority:
            if self.priority.fold == True:
                self.prior.next = self.priority.next
                continue
            bet_ = self.priority.game_action_player()
            if bet_[0] == "raise":
                self.priority.place_bet(bet_[1])
                self.pot += bet_[1]
                self.player_priority_action = bet_[1]
                self.player_priority = self.priority
            elif bet_[1] == "call":
                self.priority.place_bet(bet_[1])
                self.set_pot(bet_[1])
            elif bet_[1] == "fold":
                self.priority.fold = True
            print(self.priority.name, bet_[0], self.pot)
            self.prior = self.priority
            self.priority = self.priority.next    
        self.which_stage += 1
        self.priority = self.priority.next

    def stage(self):
        print(self.stage_public[self.which_stage])
        if self.which_stage == 1:               # Ready to see the flop
            self.deal_flop()
        if self.which_stage == 2:
            self.deal_one_card()
        if self.which_stage == 3:
            self.deal_one_card()
        
    def print_cards(self, card):
        if card[0] == 'clubs':
            return card[1], '\u2663'
        if card[0] == 'diamonds':
            return card[1], '\u2666'
        if card[0] == 'spades':
            return card[1], '\u2660'
        if card[0] == 'hearts':
            return card[1], '\u2665'
    
    def get_pot(self):
        return self.pot

    def set_pot(self, amount):
        self.pot += amount

    def reset_pot(self):
        self.pot = 0

    def payout_pot(self, list):
        pass

class Player_instance:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.next = None
        self.card1 = None
        self.card2 = None

        self.posted_blind = None
        self.bet_this_round = 0
        self.all_in = False
        self.fold = False

    def game_action_player(self):
        # Decide what to do, currently random game actions
        x = random.randint(0, 2)
        if x == 0: return ["raise", 10]
        if x == 1: return ["call", 0]
        if x == 2: 
            self.fold = True
            return ["fold", 0]

    def place_bet(self, amount):
        # Reason to place bet
        self.set_money(amount)
        self.bet_this_round += amount
        return amount

    def get_money(self):
        return self.money

    def set_money(self, amount):            # Needs work
        if self.money < amount:
            x = self.money
            self.money = 0
            self.all_in = True
            return x
        else:
            self.money += amount 
        
    def memory(self):
        pass
   
new_round = Game_instance(6,2,4)
x = 10

new_round.create_game()
new_round.play_game()