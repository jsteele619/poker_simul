from deck import new_deck
import random
import copy

class Game_instance:
    def __init__(self, num_players, small, big):
        self.num_players = num_players
        self.player_instances = []
        self.deck = new_deck
        self.update_deck = new_deck
        self.big_blind_amount = big
        self.small_blind_amount = small
        self.head = None
        self.cards_public = None
        self.cards_private = None

    def create_game(self):
        for x in range(self.num_players):
            player = Player_instance('Player ' + str(x), 100)
            self.player_instances.append(player)
            
    def play_game(self):
        self.create_game_order()
        self.post_blinds()
        self.deal_cards()
        
        
        

    def create_game_order(self):
        # Game order created with linked list indicating "button", "small blind", and "big blind"
        self.head = self.player_instances[0]
        
        for i in range(0, self.num_players - 1):
            self.player_instances[i].next = self.player_instances[i+1]
            #print(self.player_instances[i].next.name)
    
        self.player_instances[-1].next = self.player_instances[0]
        self.small_blind = self.head.next
        self.big_blind = self.head.next.next
    
        #print(self.player_instances[-1].next.name)
        #print(self.small_blind.name, self.big_blind.name)

    def post_blinds(self):
        self.small_blind.money -= self.small_blind_amount
        self.big_blind.money -= self.big_blind_amount
        if self.big_blind.money < 0: self.big_blind.money = 0
        if self.small_blind.money < 0: self.small_blind.money = 0
        
        # print(self.big_blind.name, self.big_blind.money)

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

    def print_cards(self, card):
        if card[0] == 'clubs':
            return card[1], '\u2663'
        if card[0] == 'diamonds':
            return card[1], '\u2666'
        if card[0] == 'spades':
            return card[1], '\u2660'
        if card[0] == 'hearts':
            return card[1], '\u2665'
        
class Player_instance:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.next = None
        self.card1 = None
        self.card2 = None
        self.public_hand = None
   
esp = Game_instance(6,2,4)
esp.create_game()
esp.play_game()