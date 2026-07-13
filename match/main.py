from .setup import create_matches
from .setup import create_human_match

def main():
    matches = create_matches("json_data/players.json", "json_data/matchups.json")

    human_match = create_human_match("json_data/players.json")

    human_match.start_match()

  #  matches[0].start_match()

if __name__ == "__main__":
    main()