import json
import pandas as pd
from w101_effects import Effect
from w101_effects import Damage
from w101_effects import Ward
from w101_effects import Charm
from w101_player import Player

class Match:
    def __init__(self, p1, p2, turn):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn

        self.p1e = []
        self.p2e = []

    def getPlayer1(self):
        return self.p1
    
    def getPlayer2(self):
        return self.p2
        
    def add_charm(self, spell):

        blade = Effect(
            effect_type = "CHARM",
            value = getCurrentSpell().effects.charm.value

        )
    
    def add_ward(self, target, spell):
        ward = Effect(
            effect_type = "WARD",
            value = getCurrentSpell().effects.ward.value
        )
        target.add_effect(ward)

    def add_effect(self, target_obj, effect):

        # effect = Effect(
        #     effect_type = spell_effects.get("")
        #     value = spell.effects.ward.value
        # )
        target_obj.add_effect(effect)

    def getTTarget(self, caster, target):
        if caster ==  target:
            return self.caster
        else:
            return target

# class Player:
#     def __init__(
#             self, 
#             name, 
#             school,
#             secondary_school, 
#             max_health, 
#             curr_health, 
#             pips
#         ):
#         self.name = name
#         self.school = school
#         self.secondary_school = secondary_school

#         self.max_health = max_health
#         self.curr_health = curr_health

#         self.pips = pips

#         self.effects = []

        # if any(x in ["WARD", "MANIPULATION", "AURA"] for x in spell_type):
        #     spell_effects = spell_data.get("EFFECTS")
        #     print(spell_effects)
        #     tommy = Effect(spell_type, spell_data)
        #    # print(tommy)
        #     effect_obj = tommy.get_effect_obj()
        #     print(tommy.get_effect_obj())

            #     blade = Effect(
    #         effect_type = "CHARM",
    #         value = getCurrentSpell().effects.charm.value

    #     )

 
    # spelle = spell_lookup.get(spell_name)
    # school = spelle.get("SCHOOL") if spelle else None