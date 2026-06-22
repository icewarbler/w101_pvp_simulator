import json
import pandas as pd
from w101_effects import Effect
from w101_effects import Damage
from w101_effects import Trap
from w101_effects import Charm
from w101_player import Player

class Match:
    def __init__(self, p1, p2, turn):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn

        # self.p1e = []
        # self.p2e = []

    def getPlayer1(self):
        return self.p1
    
    def getPlayer2(self):
        return self.p2
        
    def add_charm(self, spell):

        blade = Effect(
            effect_type = "CHARM",
            value = getCurrentSpell().effects.charm.value

        )
    
    # def add_ward(self, target, spell):
    #     ward = Effect(
    #         effect_type = "WARD",
    #         value = getCurrentSpell().effects.ward.value
    #     )
    #     target.add_effect(ward)

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

    # def get_p1_effects(self):
    #     return self.p1e
    
    # def get_p2_effects(self):
    #     return self.p2e

    # def delete_effect(self, target):
    #     if target == "p1":

