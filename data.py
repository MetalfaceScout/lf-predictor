#Get all data, parse it into something useful

#1. get into lfstats database
#2. Pull all scorecards down? avg mvp most important
#3. pull all games down
#4. For all games, pull mvp for each player and labels and stuff
#5. ??? eZ?

import psycopg2
import os
import json
import datetime
import decimal

lfstats_db_parameters = {
    "dbname": "lfstats",
    "user" : "u_rwjblhxb4vejjcaxrxtbavcnni",
    "password" : "yeqCN1Bh4HQm64iZpJ8tbF1TqFh7pPNHEGHSohJcYbbDyZ4eTbJoMxJY8Jg9pcom",
    "host" : "p.wqf7x2uqc5hrdcuzogrgzydf4a.db.postgresbridge.com",
    "port" : "5432",
}

class DatabaseParameters:
    def __init__(self, cursor, database_connection):
        self.cursor = cursor
        self.database_connection = database_connection

class PlayerStats:
    def __init__(self, player_name, player_team, player_id, player_position, commander_stats, heavy_stats, scout_stats, ammo_stats, medic_stats):
        self.player_name = player_name
        self.player_team = player_team
        self.player_id = player_id
        self.player_position = player_position
        self.commander_stats = commander_stats
        self.heavy_stats = heavy_stats
        self.scout_stats = scout_stats
        self.ammo_stats = ammo_stats
        self.medic_stats = medic_stats

    def __str__(self):
        string = f"Player {self.player_name} on team {self.player_team} PLAYING {self.player_position} stats:\n"
        string += self.commander_stats.__str__()
        string += self.heavy_stats.__str__()
        string += self.scout_stats.__str__()
        string += self.ammo_stats.__str__()
        string += self.medic_stats.__str__()
        return string
    
class CommanderStats:
    def __init__(self, avg_score, avg_mvp, avg_acc, hit_diff, avg_missiles, avg_medic_hits, games_played):
        self.avg_score = avg_score
        self.avg_mvp = avg_mvp
        self.avg_acc = avg_acc
        self.hit_diff = hit_diff
        self.avg_missiles = avg_missiles
        self.avg_medic_hits = avg_medic_hits
        self.games_played = games_played

    def __str__(self):
        string = "Commander:"
        string += f"Score: {self.avg_score}\nMVP: {self.avg_mvp}\n Acc: {self.avg_acc}\nHitDiff: {self.hit_diff}\nMissiles: {self.avg_missiles}\nMedicHits: {self.avg_medic_hits}\n"
        return string

class HeavyStats:
    def __init__(self, avg_score, avg_mvp, avg_acc, hit_diff, avg_missiles, avg_medic_hits, games_played):
        self.avg_score = avg_score
        self.avg_mvp = avg_mvp
        self.avg_acc = avg_acc
        self.hit_diff = hit_diff
        self.avg_missiles = avg_missiles
        self.avg_medic_hits = avg_medic_hits
        self.games_played = games_played

    def __str__(self):
        string = "Heavy:"
        string += f"Score: {self.avg_score}\nMVP: {self.avg_mvp}\n Acc: {self.avg_acc}\nHitDiff: {self.hit_diff}\nMissiles: {self.avg_missiles}\nMedicHits: {self.avg_medic_hits}\n"
        return string
    
class ScoutStats:
    def __init__(self, avg_score, avg_mvp, avg_acc, hit_diff, avg_3hit_hits, avg_medic_hits, avg_rapid_fire, games_played):
        self.avg_score = avg_score
        self.avg_mvp = avg_mvp
        self.avg_acc = avg_acc
        self.hit_diff = hit_diff
        self.avg_3hit_hits = avg_3hit_hits
        self.avg_medic_hits = avg_medic_hits
        self.avg_rapid_fire = avg_rapid_fire
        self.games_played = games_played

    def __str__(self):
        string = "Scout:"
        string += f"Score: {self.avg_score}\nMVP: {self.avg_mvp}\n Acc: {self.avg_acc}\nHitDiff: {self.hit_diff}\nMedicHits: {self.avg_medic_hits}\n3Hit: {self.avg_3hit_hits}\nRapidFire: {self.avg_rapid_fire}\n"
        return string

class AmmoStats:
    def __init__(self, avg_score, avg_mvp, avg_acc, hit_diff, avg_boosts, avg_resups, games_played):
        self.avg_score = avg_score
        self.avg_mvp = avg_mvp
        self.avg_acc = avg_acc
        self.hit_diff = hit_diff
        self.avg_boosts = avg_boosts
        self.avg_resups = avg_resups
        self.games_played = games_played

    def __str__(self):
        string = "Ammo:"
        string += f"Score: {self.avg_score}\nMVP: {self.avg_mvp}\n Acc: {self.avg_acc}\nHitDiff: {self.hit_diff}\nBoosts: {self.avg_boosts}\nResups: {self.avg_resups}\n"
        return string

class MedicStats:
    def __init__(self, avg_score, avg_mvp, avg_acc, hit_diff, avg_boosts, avg_resups, avg_lives_left, team_elim_rate, games_played):
        self.avg_score = avg_score
        self.avg_mvp = avg_mvp
        self.avg_acc = avg_acc
        self.hit_diff = hit_diff
        self.avg_boosts = avg_boosts
        self.avg_resups = avg_resups
        self.avg_lives_left = avg_lives_left
        self.team_elim_rate = team_elim_rate
        self.games_played = games_played

    def __str__(self):
        string = "Medic:"
        string += f"Score: {self.avg_score}\nMVP: {self.avg_mvp}\n Acc: {self.avg_acc}\nHitDiff: {self.hit_diff}\nBoosts: {self.avg_boosts}\nResups: {self.avg_resups}\nLivesLeft: {self.avg_lives_left}\nTeamElimRate: {self.team_elim_rate}\n"
        return string

        
    
class LaserTagGame:
    def __init__(self, game_id, center_id, winner):
        self.game_id = game_id
        self.center_id = center_id
        self.winner = winner
        self.player_green_commander = 0
        self.player_green_heavy = 0
        self.player_green_scout = 0
        self.player_green_scout_2 = 0
        self.player_green_ammo = 0
        self.player_green_medic = 0
        self.player_red_commander = 0
        self.player_red_heavy = 0
        self.player_red_scout = 0
        self.player_red_scout_2 = 0
        self.player_red_ammo = 0
        self.player_red_medic = 0
    
    def __str__(self):
        string = "Game:\n"
        string += self.winner
        string += self.player_green_commander.__str__()
        string += self.player_green_heavy.__str__()
        string += self.player_green_scout.__str__()
        string += self.player_green_scout_2.__str__()
        string += self.player_green_ammo.__str__()
        string += self.player_green_medic.__str__()
        string += self.player_red_commander.__str__()
        string += self.player_red_heavy.__str__()
        string += self.player_red_scout.__str__()
        string += self.player_red_scout_2.__str__()
        string += self.player_red_ammo.__str__()
        string += self.player_red_medic.__str__()
        return string
        
    

def initalize_connection():
    database_connection = psycopg2.connect(**lfstats_db_parameters)
    cursor = database_connection.cursor()
    params = DatabaseParameters(cursor, database_connection)
    return params

def close_connection(db : DatabaseParameters):
    db.cursor.close()
    db.database_connection.close()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Converts to ISO 8601 string
        elif isinstance(obj, datetime.date):
            return obj.isoformat()  # Converts date to ISO format
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        return super().default(obj)

def datetime_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                if value.replace(".", "", 1).isdigit():  # Check if it's a decimal-like string
                    dct[key] = decimal.Decimal(value)  # Convert back to Decimal
                else:
                    dct[key] = datetime.datetime.fromisoformat(value)  # Convert datetime strings
            except ValueError:
                pass  # Keep original value if conversion fails
    return dct

def fill_games_from_scorecards(db : DatabaseParameters, games : list[LaserTagGame]): 

    scorecards_cache = {}

    if os.path.exists("scorecards.json"):
        with open("scorecards.json", "r") as file:
            scorecards_cache = json.load(file, object_hook=datetime_decoder)
    else:
        scorecards = db.cursor.execute("SELECT * FROM scorecards")
        scorecards_cache["scorecards"] = db.cursor.fetchall()
        with open("scorecards.json", "w") as file:
            json.dump(scorecards_cache, file, indent=4, cls=DateTimeEncoder)

    all_games = []

    mvp_cache = {}

    for game in games:

        players_in_game = []

        game = LaserTagGame(game.game_id, game.center_id, game.winner)

        for scorecard in scorecards_cache["scorecards"]:
            if scorecard[42] == game.game_id:
                players_in_game.append(scorecard)
        
        if len(players_in_game) != 12:
            continue

        all_player_team_stats = []

        for player in players_in_game:

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

            for scorecard in scorecards_cache["scorecards"]:
                if scorecard[45] == player[45] and scorecard[2] <= player[2]: # date is less than game date:
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
                player_name= player[1],
                player_team= player[3],
                player_id= player[0],
                player_position= player[4],
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
            player_stats.player_position = player[4]
            all_player_team_stats.append(player_stats)

        red_team_players = []
        green_team_players = []
        for player in all_player_team_stats:
            if player.player_team == "red":
                red_team_players.append(player)
            else:
                green_team_players.append(player)
        
        for player in red_team_players:
            if player.player_position == "Commander":
                game.player_red_commander = player
                continue
            if player.player_position == "Heavy Weapons":
                game.player_red_heavy = player
                continue
            if player.player_position == "Scout":
                if isinstance(game.player_red_scout, PlayerStats):
                    game.player_red_scout_2 = player
                else:
                    game.player_red_scout = player
                continue
            if player.player_position == "Ammo Carrier":
                game.player_red_ammo = player
                continue
            if player.player_position == "Medic":
                game.player_red_medic = player
                continue

        for player in green_team_players:
            if player.player_position == "Commander":
                game.player_green_commander = player
                continue
            if player.player_position == "Heavy Weapons":
                game.player_green_heavy = player
                continue
            if player.player_position == "Scout":
                if isinstance(game.player_green_scout, PlayerStats):
                    game.player_green_scout_2 = player
                else:
                    game.player_green_scout = player
                continue
            if player.player_position == "Ammo Carrier":
                game.player_green_ammo = player
                continue
            if player.player_position == "Medic":
                game.player_green_medic = player
                continue

        all_games.append(game)
        print(f"Games Processed: {len(all_games)}")

    return all_games

def create_csv_from_games(games: list[LaserTagGame]):
    with open("game_data.csv", "w") as file:
        file.write("" +
        "id," + 
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
        "red_medic_score, red_medic_mvp, red_medic_acc, red_medic_hit_diff, red_medic_boosts, red_medic_resups, red_medic_lives_left, red_medic_elim_rate, red_medic_games_played," +
        "winner\n")
        for game in games:
            
            if isinstance(game.player_green_commander, int):
                continue

            if isinstance(game.player_green_heavy, int):
                continue

            if isinstance(game.player_green_scout, int):
                continue

            if isinstance(game.player_green_scout_2, int):
                continue

            if isinstance(game.player_green_medic, int):
                continue

            if isinstance(game.player_red_commander, int):
                continue

            if isinstance(game.player_red_heavy, int):
                continue

            if isinstance(game.player_red_scout, int):
                continue

            if isinstance(game.player_red_scout_2, int):
                continue

            if isinstance(game.player_red_ammo, int):
                continue

            if isinstance(game.player_red_medic, int):
                continue

            
            string = f"{game.game_id},"

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
            string += f"{medic.games_played},"

            string += f"{game.winner}\n"
            file.write(string)
    

def retrieve_all_games(db):
    db.cursor.execute("SELECT id, center_id, winner FROM games;")
    games = db.cursor.fetchall()
    
    all_games = []

    for game in games:
        ltgame = LaserTagGame(game[0], game[1], game[2])
        all_games.append(ltgame)
    return all_games



if __name__ == "__main__":
    db = initalize_connection()
    games = retrieve_all_games(db)

    filled_games = fill_games_from_scorecards(db, games)

    create_csv_from_games(filled_games)

    close_connection(db)