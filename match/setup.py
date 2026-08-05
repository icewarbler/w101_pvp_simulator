import json
from .player import Player
from .match import Match
from .dataloader import load_json
from .deck import Deck

def create_matches(players_file, matchups_file):
    players = load_json(players_file)
    matchups = load_json(matchups_file)

    player_lookup = { player["NAME"]: player for player in players }

    matches = []

    for matchup in matchups:
        p1_dat = player_lookup[matchup["PLAYER1"]]
        p2_dat = player_lookup[matchup["PLAYER2"]]

        p1 = create_player(p1_dat)
        p2 = create_player(p2_dat)

        matches.append(Match(p1, p2, 0, matchup["MATCH_FILE"]))

    return matches

def create_human_match(players_file):
    players = load_json(players_file)

    player_lookup = { player["NAME"]: player for player in players }
    
    player1_name = input("Player 1 name: ").upper()
    player2_name = input("Player 2 name: ").upper()
    p1_dat = player_lookup[player1_name]
    p2_dat = player_lookup[player2_name]

    p1 = create_player(p1_dat, True)
    p2 = create_player(p2_dat, True)

    return Match(p1, p2, 0)

def create_player(player_data, deck=False):
    decks = load_json("json_data/decks.json")

    deck_lookup = { deck["SCHOOL"]: deck for deck in decks }

    p_deck = deck_lookup[player_data["SCHOOL"]]

 #   print(p_deck["SPELLS"])

 #   my_deck = Deck(p_deck["SPELLS"])

    if deck:
        return Player(
            player_data["NAME"],
            player_data["SCHOOL"],
            player_data["SECONDARYSCHOOL"],
            player_data["LEVEL"],
            player_data["MAX_HEALTH"],
            player_data["OUTGOING_DAMAGE"],
            player_data["INCOMING_RESIST"],
            player_data["PIERCE"],
            p_deck
           # player_data["DECK"]
        )
    else:
        return Player(
            player_data["NAME"],
            player_data["SCHOOL"],
            player_data["SECONDARYSCHOOL"],
            player_data["LEVEL"],
            player_data["MAX_HEALTH"],
            player_data["OUTGOING_DAMAGE"],
            player_data["INCOMING_RESIST"],
            player_data["PIERCE"]
        )