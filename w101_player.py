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
            level,
            max_health
        ):
        self.name = name
        self.school = school
        self.secondary_school = secondary_school

        self.level = level

        self.max_health = max_health

        self.curr_health = max_health

        self.pips = []

        self.effects = []
    
    def add_effect(self, effect):
        self.effects.append(effect)

    def get_effects(self):
        return self.effects
    
    def get_health(self):
        return self.curr_health
    
    def dec_health(self, value):
        self.curr_health -= value

    def del_effect(self, effect):
        self.effects.remove(effect)
        

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