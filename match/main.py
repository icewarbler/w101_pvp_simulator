from .setup import create_matches
from .setup import create_human_match

def main():
    chooser = input("Play your own match? Y/N: ").upper()

    if chooser == "Y":
        human_match = create_human_match("json_data/players.json")
        human_match.start_match()

    else:
        matches = create_matches("json_data/players.json", "json_data/matchups.json")
        spec_match = input("Play match 0 or match 1? ")
        matches[int(spec_match)].start_match()

  #  human_match = create_human_match("json_data/players.json")

  #  human_match.start_match()

 #   matches[0].start_match()

if __name__ == "__main__":
    main()