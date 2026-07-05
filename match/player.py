from effects import Effect
import pandas as pd
import json

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

        # Balance
        # Death
        # Fire
        # Ice
        # Life
        # Myth
        # Storm
        # Reg
        # Power
        self.pips = []
        self.shadpips = 0

        self.selected_school = school

        self.effects = []

        self.aura = None

        self.backlash = None

    
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
    
    def explode_dot(self, dot, multiplier):
        res = self.incoming_resist[dot.school]
        res -= dot.pierce_val
        res = 0 if res < 0 else res
        dot.leftover_value =  dot.leftover_value * multiplier * 0.01
        dot.leftover_value *= (1 - res * 0.01)
        self.dec_health(dot.leftover_value)
        print(f"{self.name} took {dot.leftover_value} damage from dot")
        self.del_effect(dot)

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

    def last_pip_index(self, school):
        return next((i for i in range(len(self.pips) - 1, -1, -1) if self.pips[i].school == school), None)
    
    def sort_pips(self):
        reg = [pip for pip in self.pips if pip.school == "REG"]
        power = [pip for pip in self.pips if pip.school == "POWER"]
        school = [pip for pip in self.pips if pip.school not in ("REG", "POWER")]
        school.sort(key=lambda pip: pip.school)
        self.pips = reg + power + school

    def remove_pip(self, pip):
        self.pips.remove(pip)

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