from .setup import create_matches

def main():
    matches = create_matches("json_data/players.json", "json_data/matchups.json")

    matches[0].start_match()

if __name__ == "__main__":
    main()