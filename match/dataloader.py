import json

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("ERROR! FAILED TO DECODE JSON!")