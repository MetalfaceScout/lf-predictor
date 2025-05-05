from data import PlayerStats
from data import CommanderStats
from data import HeavyStats
from data import ScoutStats
from data import AmmoStats
from data import MedicStats
from data import LaserTagGame

from data import lfstats_db_parameters
from data import initalize_connection
from data import close_connection

from data import DatabaseParameters

import pandas as pd
import tensorflow as tf
import keras
import psycopg2

import util

import io
import argparse

model_filename = "selector_model.keras"

def main():

    parser = argparse.ArgumentParser(description="Predict the outcome of a laser tag game.")
    parser.add_argument("--player", nargs=3, type=int, action="append")
    args = parser.parse_args()

    db = initalize_connection()

    game = LaserTagGame(0, 17, "Unknown")

    for player_arg in args.player:
        assign_to_game(db, player_arg, game)

    print(game)
    dataframe = util.create_data(game)

    model = keras.saving.load_model(model_filename)

    y_hat = model.predict(dataframe)
    print(y_hat)

    close_connection(db)            


def match_to_game(game, position_id, team, player_stats):
    if team == 0:
        match position_id:
            case 0: #Commander
                game.player_red_commander = player_stats.commander_stats
            case 1: #Heavy Weapons
                game.player_red_heavy = player_stats.heavy_stats
            case 2: #Scout
                game.player_red_scout = player_stats.scout_stats
            case 3: #Scout 2
                game.player_red_scout_2 = player_stats.scout_stats
            case 4: #Ammo
                game.player_red_ammo = player_stats.ammo_stats
            case 5: #Medic
                game.player_red_medic = player_stats.medic_stats
    else:
        match position_id:
            case 0: #Commander
                game.player_red_commander = player_stats.commander_stats
            case 1: #Heavy Weapons
                game.player_red_heavy = player_stats.heavy_stats
            case 2: #Scout
                game.player_red_scout = player_stats.scout_stats
            case 3: #Scout 2
                game.player_red_scout_2 = player_stats.scout_stats
            case 4: #Ammo
                game.player_red_ammo = player_stats.ammo_stats
            case 5: #Medic
                game.player_red_medic = player_stats.medic_stats

def assign_to_game(db, argument, game):
    player_stats = make_stats(db, argument[0])
    match_to_game(game, argument[1], argument[2], player_stats)

# Take a player name and return a full PlayerStats object.
def make_stats(db, player_id):
    stats = util.parse_player(db, player_id)
    return stats

if __name__ == "__main__":
    main()