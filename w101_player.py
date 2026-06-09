from w101_effects import Effect
import pandas as pd
import json

# try:
#     with open("w101_spells_schema.json", "r") as f:
#         spells = json.load(f)
#     print("File data =", spells)
# except json.JSONDecodeError:
#     print("Error: failed to decode JSON")

# spells_df = pd.DataFrame(spells)

class Player:
    def __init__(
            self, 
            name, 
            school,
            secondary_school, 
            max_health, 
            curr_health, 
            pips
        ):
        self.name = name
        self.school = school
        self.secondary_school = secondary_school

        self.max_health = max_health
        self.curr_health = curr_health

        self.pips = pips

        self.effects = []
        

    # def add_blade(self):

    #     blade = Effect(
    #         effect_type = "CHARM",
    #         value = getCurrentSpell().effects.charm.value

    #     )

        # self.outgoing_damage = {
        #     "FIRE": 0,
        #     "ICE": 0,
        #     "STORM": 0,
        #     "LIFE": 0,
        #     "DEATH": 0,
        #     "MYTH": 0,
        #     "BALANCE": 0
        # }
        # self.incoming_resist = {
        #     "FIRE": 0,
        #     "ICE": 0,
        #     "STORM": 0,
        #     "LIFE": 0,
        #     "DEATH": 0,
        #     "MYTH": 0,
        #     "BALANCE": 0
        # }