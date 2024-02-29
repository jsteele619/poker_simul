import poker

def game_time():
    new_round = poker.Game_instance(8, 2, 4)
    new_round.create_game()
    new_round.create_game_order()
    new_round.define_position()
    for x in range(10):    
        
        new_round.play_game()
        new_round.rotate_game_order()
        new_round.define_position
        new_round.reset_priority()
        new_round.reset_pot
        print(x)

    new_round.print_csv()

game_time()