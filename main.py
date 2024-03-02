import poker
import pandas as pd

def game_time():
    new_round = poker.Game_instance(8, 2, 4)        # Num Players, Small Blind, Big Blind
    new_round.create_game()
    new_round.create_game_order()
    new_round.define_position()
    df = new_round.create_pandas_df()
    for x in range(10):    
        new_round.play_game()
    print(df)
    player_list = new_round.print_csv()

game_time()