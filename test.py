import psycopg2
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

import io

model_filename = "selector_model.keras"

def main():

    with open("test_team.txt", "r",) as team_file:
        red_commander_name = team_file.readline().rstrip()
        red_heavy_name = team_file.readline().rstrip()
        red_scout_1_name = team_file.readline().rstrip()
        red_scout_2_name = team_file.readline().rstrip()
        red_ammo_name = team_file.readline().rstrip()
        red_medic_name = team_file.readline().rstrip()

        spacer = team_file.readline()
        if spacer != "\n":
            raise Exception("file format is incorrect. No space between teams.")

        green_commander_name = team_file.readline().rstrip()
        green_heavy_name = team_file.readline().rstrip()
        green_scout_1_name = team_file.readline().rstrip()
        green_scout_2_name = team_file.readline().rstrip()
        green_ammo_name = team_file.readline().rstrip()
        green_medic_name = team_file.readline().rstrip()

    db = initalize_connection()

    red_commander_stats = make_stats(db, red_commander_name)
    red_heavy_stats = make_stats(db, red_heavy_name)
    red_scout_1_stats = make_stats(db, red_scout_1_name)
    red_scout_2_stats = make_stats(db, red_scout_2_name)
    red_ammo_stats = make_stats(db, red_ammo_name)
    red_medic_stats = make_stats(db, red_medic_name)

    green_commander_stats = make_stats(db, green_commander_name)
    green_heavy_stats = make_stats(db, green_heavy_name)
    green_scout_1_stats = make_stats(db, green_scout_1_name)
    green_scout_2_stats = make_stats(db, green_scout_2_name)
    green_ammo_stats = make_stats(db, green_ammo_name)
    green_medic_stats = make_stats(db, green_medic_name)

    game = LaserTagGame(0, 17, 0)

    game.player_red_commander = red_commander_stats
    game.player_red_heavy = red_heavy_stats
    game.player_red_scout = red_scout_1_stats
    game.player_red_scout_2 = red_scout_2_stats
    game.player_red_ammo = red_ammo_stats
    game.player_red_medic = red_medic_stats

    game.player_green_commander = green_commander_stats
    game.player_green_heavy = green_heavy_stats
    game.player_green_scout = green_scout_1_stats
    game.player_green_scout_2 = green_scout_2_stats
    game.player_green_ammo = green_ammo_stats
    game.player_green_medic = green_medic_stats

    dataframe = create_data(game)

    model = keras.saving.load_model(model_filename)

    y_hat = model.predict(dataframe)
    print(y_hat)

    close_connection(db)

#Return a TF dataframe from a laser tag game properly formatted to fit the model.
def create_data(game):
    string = (
        "green_commander_score, green_commander_mvp, green_commander_acc, green_commander_hit_diff, green_commander_missiles, green_commander_medic_hits, green_commander_games_played," +
        "green_heavy_score, green_heavy_mvp, green_heavy_avg_acc, green_heavy_hit_diff, green_heavy_missiles, green_heavy_medic_hits, green_heavy_games_played," + 
        "green_scout_score, green_scout_mvp, green_scout_acc, green_scout_hit_diff, green_scout_3hit, green_scout_medic_hits, green_scout_rapid_fire, green_scout_games_played," +
        "green_scout2_score, green_scout2_mvp, green_scout2_acc, green_scout2_hit_diff, green_scout2_3hit, green_scout2_medic_hits, green_scout2_rapid_fire, green_scout2_games_played," +
        "green_ammo_score, green_ammo_mvp, green_ammo_acc, green_ammo_hit_diff, green_ammo_boosts, green_ammo_resups, green_ammo_games_played," +
        "green_medic_score, green_medic_mvp, green_medic_acc, green_medic_hit_diff, green_medic_boosts, green_medic_resups, green_medic_lives_left, green_medic_elim_rate, green_medic_games_played," +
        "red_commander_score, red_commander_mvp, red_commander_acc, red_commander_hit_diff, red_commander_missiles, red_commander_medic_hits, red_commander_games_played," +
        "red_heavy_score, red_heavy_mvp, red_heavy_avg_acc, red_heavy_hit_diff, red_heavy_missiles, red_heavy_medic_hits, red_heavy_games_played," + 
        "red_scout_score, red_scout_mvp, red_scout_acc, red_scout_hit_diff, red_scout_3hit, red_scout_medic_hits, red_scout_rapid_fire, red_scout_games_played," +
        "red_scout2_score, red_scout2_mvp, red_scout2_acc, red_scout2_hit_diff, red_scout2_3hit, red_scout2_medic_hits, red_scout2_rapid_fire, red_scout2_games_played," +
        "red_ammo_score, red_ammo_mvp, red_ammo_acc, red_ammo_hit_diff, red_ammo_boosts, red_ammo_resups, red_ammo_games_played," +
        "red_medic_score, red_medic_mvp, red_medic_acc, red_medic_hit_diff, red_medic_boosts, red_medic_resups, red_medic_lives_left, red_medic_elim_rate, red_medic_games_played" +
        "\n")
    commander = game.player_green_commander.commander_stats
    string += f"{commander.avg_score},"
    string += f"{commander.avg_mvp},"
    string += f"{commander.avg_acc},"
    string += f"{commander.hit_diff},"
    string += f"{commander.avg_missiles},"
    string += f"{commander.avg_medic_hits},"
    string += f"{commander.games_played},"

    heavy = game.player_green_heavy.heavy_stats
    string += f"{heavy.avg_score},"
    string += f"{heavy.avg_mvp},"
    string += f"{heavy.avg_acc},"
    string += f"{heavy.hit_diff},"
    string += f"{heavy.avg_missiles},"
    string += f"{heavy.avg_medic_hits},"
    string += f"{heavy.games_played},"

    scout = game.player_green_scout.scout_stats   
    string += f"{scout.avg_score},"
    string += f"{scout.avg_mvp},"
    string += f"{scout.avg_acc},"
    string += f"{scout.hit_diff},"
    string += f"{scout.avg_3hit_hits},"
    string += f"{scout.avg_medic_hits},"
    string += f"{scout.avg_rapid_fire},"
    string += f"{scout.games_played},"

    scout = game.player_green_scout_2.scout_stats   
    string += f"{scout.avg_score},"
    string += f"{scout.avg_mvp},"
    string += f"{scout.avg_acc},"
    string += f"{scout.hit_diff},"
    string += f"{scout.avg_3hit_hits},"
    string += f"{scout.avg_medic_hits},"
    string += f"{scout.avg_rapid_fire},"
    string += f"{scout.games_played},"

    ammo = game.player_green_ammo.ammo_stats
    string += f"{ammo.avg_score},"
    string += f"{ammo.avg_mvp},"
    string += f"{ammo.avg_acc},"
    string += f"{ammo.hit_diff},"
    string += f"{ammo.avg_boosts},"
    string += f"{ammo.avg_resups},"
    string += f"{ammo.games_played},"

    medic = game.player_green_medic.medic_stats
    string += f"{medic.avg_score},"
    string += f"{medic.avg_mvp},"
    string += f"{medic.avg_acc},"
    string += f"{medic.hit_diff},"
    string += f"{medic.avg_boosts},"
    string += f"{medic.avg_resups},"
    string += f"{medic.avg_lives_left},"
    string += f"{medic.team_elim_rate},"
    string += f"{medic.games_played},"

    commander = game.player_red_commander.commander_stats
    string += f"{commander.avg_score},"
    string += f"{commander.avg_mvp},"
    string += f"{commander.avg_acc},"
    string += f"{commander.hit_diff},"
    string += f"{commander.avg_missiles},"
    string += f"{commander.avg_medic_hits},"
    string += f"{commander.games_played},"

    heavy = game.player_red_heavy.heavy_stats
    string += f"{heavy.avg_score},"
    string += f"{heavy.avg_mvp},"
    string += f"{heavy.avg_acc},"
    string += f"{heavy.hit_diff},"
    string += f"{heavy.avg_missiles},"
    string += f"{heavy.avg_medic_hits},"
    string += f"{heavy.games_played},"

    scout = game.player_red_scout.scout_stats   
    string += f"{scout.avg_score},"
    string += f"{scout.avg_mvp},"
    string += f"{scout.avg_acc},"
    string += f"{scout.hit_diff},"
    string += f"{scout.avg_3hit_hits},"
    string += f"{scout.avg_medic_hits},"
    string += f"{scout.avg_rapid_fire},"
    string += f"{scout.games_played},"

    scout = game.player_red_scout_2.scout_stats   
    string += f"{scout.avg_score},"
    string += f"{scout.avg_mvp},"
    string += f"{scout.avg_acc},"
    string += f"{scout.hit_diff},"
    string += f"{scout.avg_3hit_hits},"
    string += f"{scout.avg_medic_hits},"
    string += f"{scout.avg_rapid_fire},"
    string += f"{scout.games_played},"

    ammo = game.player_red_ammo.ammo_stats
    string += f"{ammo.avg_score},"
    string += f"{ammo.avg_mvp},"
    string += f"{ammo.avg_acc},"
    string += f"{ammo.hit_diff},"
    string += f"{ammo.avg_boosts},"
    string += f"{ammo.avg_resups},"
    string += f"{ammo.games_played},"

    medic = game.player_red_medic.medic_stats
    string += f"{medic.avg_score},"
    string += f"{medic.avg_mvp},"
    string += f"{medic.avg_acc},"
    string += f"{medic.hit_diff},"
    string += f"{medic.avg_boosts},"
    string += f"{medic.avg_resups},"
    string += f"{medic.avg_lives_left},"
    string += f"{medic.team_elim_rate},"
    string += f"{medic.games_played}"

    #string += f"{game.winner}\n"
    
    dataframe = pd.read_csv(io.StringIO(string))

    return tf.data.Dataset.from_tensors(dataframe)

def specify_player(ids, db, player_name):
    players = {}
    center_names = {}
    for (i, id) in enumerate(ids):
        db.cursor.execute(f"SELECT center_id, player_name FROM scorecards WHERE player_id = {id[0]}")
        centers = {}
        scorecards_center_id = db.cursor.fetchall()
        for center_id in scorecards_center_id:
            if center_id[0] in centers:
                centers[center_id[0]] += 1
            else:
                centers[center_id[0]] = 1

        players[i] = centers

        for center in centers:
            db.cursor.execute(f"SELECT name FROM centers WHERE id = {center}")
            name = db.cursor.fetchall()
            center_names[center] = name[0]
    
    print(f"Two players have been found with the same name: {player_name}. Enter the number corresponding to the player you'd like to choose.")
    for player in players:
        print(f"{player}: ", end="")
        for center in players[player]:
            print(f"{center_names[center][0]} : {players[player][center]}, ", end="")
        print()

    choice = int(input())

    return ids[choice][0]

# Look for an id associated with the player and return it.
def find_player_from_name(db : DatabaseParameters, player_name):
    db.cursor.execute("SELECT player_id FROM players_names WHERE player_name ILIKE %s", (f'{player_name}',))
    ids = db.cursor.fetchall()

    if len(ids) > 1:
        return_id = specify_player(ids, db, player_name)
    else:
        return_id = ids[0][0]
    
    return return_id


# Go out on the database and fill up a PlayerStats object for that player.
def parse_player(db, id):
    db.cursor.execute(f"SELECT * FROM scorecards WHERE player_id = {id}")
    scorecards = db.cursor.fetchall()

    commander_total_score = 0
    commander_total_mvp = 0
    commander_total_acc = 0
    commander_total_hit_diff = 0
    commander_total_missiles = 0
    commander_total_medic_hits = 0

    heavy_total_score = 0
    heavy_total_mvp = 0
    heavy_total_acc = 0
    heavy_total_hit_diff = 0
    heavy_total_missiles = 0
    heavy_total_medic_hits = 0

    scout_total_score = 0
    scout_total_mvp = 0
    scout_total_acc = 0
    scout_total_hit_diff = 0
    scout_total_3hit_hits = 0
    scout_total_medic_hits = 0
    scout_total_rapid_fire = 0

    ammo_total_score = 0
    ammo_total_mvp = 0
    ammo_total_acc = 0
    ammo_total_hit_diff = 0
    ammo_total_boosts = 0
    ammo_total_resups = 0

    medic_total_score = 0
    medic_total_mvp = 0
    medic_total_acc = 0
    medic_total_hit_diff = 0
    medic_total_boosts = 0
    medic_total_resups = 0
    medic_total_lives_left = 0
    medic_team_elim_rate = 0

    total_commander_games_played = 0
    total_heavy_games_played = 0
    total_scout_games_played = 0
    total_ammo_games_played = 0
    total_medic_games_played = 0
    
    for scorecard in scorecards:
        match scorecard[4]:
            case "Commander":
                total_commander_games_played += 1
                commander_total_score += scorecard[21]
                commander_total_acc += scorecard[36]
                commander_total_hit_diff += scorecard[37]
                commander_total_medic_hits += scorecard[14]
                commander_total_mvp += scorecard[38]
                commander_total_missiles += scorecard[31]
            case "Heavy Weapons":
                total_heavy_games_played += 1
                heavy_total_score += scorecard[21]
                heavy_total_acc += scorecard[36]
                heavy_total_hit_diff += scorecard[37]
                heavy_total_medic_hits += scorecard[14]
                heavy_total_mvp += scorecard[38]
                heavy_total_missiles += scorecard[31]
            case "Scout":
                total_scout_games_played += 1
                scout_total_score += scorecard[21]
                scout_total_acc += scorecard[36]
                scout_total_hit_diff += scorecard[37]
                scout_total_medic_hits += scorecard[14]
                scout_total_mvp += scorecard[38]
                scout_total_3hit_hits += scorecard[25]
                scout_total_rapid_fire += scorecard[17]
            case "Ammo Carrier":
                total_ammo_games_played += 1
                ammo_total_score += scorecard[21]
                ammo_total_acc += scorecard[36]
                ammo_total_hit_diff += scorecard[37]
                ammo_total_mvp += scorecard[38]
                ammo_total_boosts += scorecard[19]
                ammo_total_resups += scorecard[33]
            case "Medic":
                total_medic_games_played += 1
                medic_total_score += scorecard[21]
                medic_total_acc += scorecard[36]
                medic_total_hit_diff += scorecard[37]
                medic_total_mvp += scorecard[38]
                medic_total_boosts += scorecard[18]
                medic_total_resups += scorecard[33]
                medic_total_lives_left += scorecard[20]
                medic_team_elim_rate += scorecard[26]

    if total_ammo_games_played == 0:
        total_ammo_games_played += 1
    if total_scout_games_played == 0:
        total_scout_games_played += 1
    if total_commander_games_played == 0:
        total_commander_games_played += 1
    if total_medic_games_played == 0:
        total_medic_games_played += 1
    if total_heavy_games_played == 0:
        total_heavy_games_played += 1
    player_stats = PlayerStats(
        player_name= "Name",
        player_team= "Team",
        player_id= id,
        player_position= "",
        commander_stats= CommanderStats(
            commander_total_score/total_commander_games_played,
            commander_total_mvp/total_commander_games_played,
            commander_total_acc/total_commander_games_played,
            commander_total_hit_diff/total_commander_games_played,
            commander_total_missiles/total_commander_games_played,
            commander_total_medic_hits/total_commander_games_played,
            total_commander_games_played
        ),
        heavy_stats= HeavyStats(
            heavy_total_score/total_heavy_games_played,
            heavy_total_mvp/total_heavy_games_played,
            heavy_total_acc/total_heavy_games_played,
            heavy_total_hit_diff/total_heavy_games_played,
            heavy_total_missiles/total_heavy_games_played,
            heavy_total_medic_hits/total_heavy_games_played,
            total_heavy_games_played
        ),
        scout_stats= ScoutStats(
            scout_total_score/total_scout_games_played,
            scout_total_mvp/total_scout_games_played,
            scout_total_acc/total_scout_games_played,
            scout_total_hit_diff/total_scout_games_played,
            scout_total_3hit_hits/total_scout_games_played,
            scout_total_medic_hits/total_scout_games_played,
            scout_total_rapid_fire/total_scout_games_played,
            total_scout_games_played
        ),
        ammo_stats= AmmoStats(
            ammo_total_score/total_ammo_games_played,
            ammo_total_mvp/total_ammo_games_played,
            ammo_total_acc/total_ammo_games_played,
            ammo_total_hit_diff/total_ammo_games_played,
            ammo_total_boosts/total_ammo_games_played,
            ammo_total_resups/total_ammo_games_played,
            total_ammo_games_played
        ),
        medic_stats = MedicStats(
            medic_total_score/total_medic_games_played,
            medic_total_mvp/total_medic_games_played,
            medic_total_acc/total_medic_games_played,
            medic_total_hit_diff/total_medic_games_played,
            medic_total_boosts/total_medic_games_played,
            medic_total_resups/total_medic_games_played,
            medic_total_lives_left/total_medic_games_played,
            medic_team_elim_rate/total_medic_games_played,
            total_medic_games_played
        )
    )

    return player_stats
            

# Take a player name and return a full PlayerStats object.
def make_stats(db, player_name):
    player = find_player_from_name(db, player_name)
    stats = parse_player(db, player)
    return stats

if __name__ == "__main__":
    main()