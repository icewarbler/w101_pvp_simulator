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
            max_health,
            outgoing_damage,
            incoming_resist,
            pierce
        ):
        self.name = name
        self.school = school
        self.secondary_school = secondary_school

        self.level = level

        self.max_health = max_health

        self.curr_health = max_health

        self.outgoing_damage = outgoing_damage
        self.incoming_resist = incoming_resist
        self.pierce = pierce

        self.pips = []

        self.effects = []
    
    def add_effect(self, effect):
        self.effects.append(effect)

    def get_effects(self):
        return self.effects
    
    def get_health(self):
        return self.curr_health
    
    def get_outgoing_damage(self, school):
        return self.outgoing_damage.get(school)

    def get_incoming_resist(self, school):
        return self.incoming_resist.get(school)
    #Your gear (% then flat)-> 
# your aura -> 
# your charms-> 
# the global-> 
# target's aura->
# target's wards-> 
# target's gear(flat then %)-> 
# critical 
    def dec_health(self, value):
        # a1 = value * enemy.get_outgoing_dmg
        # a2 = a1 * enemy.get_aura
        # a3 = a2 * enemy.get_charms
        # a4 = a3 * get_global
        # a5 = a4 * self.get_aura
        # a6 = a5 * self.get_wards
        # a7 = a6 * enemy.get_incoming_res
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