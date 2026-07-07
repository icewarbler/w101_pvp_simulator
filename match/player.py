from .effects import Effect
from .effects import DOT
from .effects import Bomb_DOT
import pandas as pd
import json
import math

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

        self.minion = None

    
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

    def take_backlash(self):
        if self.backlash.expired():
            perc_dmg = self.backlash.accumulated
            dmg_taken = self.max_health * (perc_dmg * 0.01)
            print(f"{self.name} takes {dmg_taken} damage!")
            self.dec_health(dmg_taken)
            print(f"{self.name} HEALTH: {math.floor(self.curr_health)}")
            self.backlash = None

    def backlash_eat(self, enemy_player):
        eat_effect = self.backlash.condition["EFFECT"]
        effect_target = self.backlash.condition["TARGET"]

        if effect_target == "SELF":
            eat_target = self
        elif effect_target == "ENEMY":
            eat_target = enemy_player
        
        ate = False

        print(f"eat_effect: {eat_effect}")
        for effect in reversed(eat_target.effects):
            if eat_effect in effect.categories:
                eat_target.del_effect(effect)
                print(f"eating effect: {effect} from {eat_target.name}")
                ate = True
                break

        if not ate:
            self.backlash.inc_backlash()
            print("Did not eat an effect")

    def activate_dots(self, match_obj):
        caster_dots = [ effect for effect in self.effects if isinstance(effect, DOT) ]

        for dot in caster_dots:
            print(f"DOT: {dot}")
            dot.tick(self, match_obj)
            dot.begin_round()

    def activate_bombs(self):
        caster_bombs = [ effect for effect in self.effects if isinstance(effect, Bomb_DOT) ]

        for dot in caster_bombs:
            print(f"DOT: {dot}")
            dot.begin_round()

    def print_effects(self):
        print(f"{self.name}:")
        for effect in self.effects:
            print(f"{effect}")

    def handle_pips(self, context):
        print(f"{self.name} has {[pip for pip in self.pips]} pips and {self.shadpips} shad pips before casting")

        priority_school = context.spell.get("SCHOOL")
        caster_school = self.school
        print(f"spell school: {priority_school}; caster school: {caster_school}")
        if caster_school == priority_school:
            use_power = True
        else:
            use_power = False

        # eats from school pips first
        for school, cost in context.schoolpips.items():
            print(f"Found a school pip: {school}")
            to_rem = next((pip for pip in self.pips if pip.school == school), None)
            if to_rem is None:
                raise AssertionError("Impossible to cast spell without required school pip(s)!")
            self.remove_pip(to_rem)

        while context.pips > 0:
            odd = True if context.pips % 2 == 1 else False

            # even number of pips means no reg pips consumed
            if not odd:
                school_pip = next((pip for pip in self.pips if pip.school == priority_school), None)
                if school_pip is not None:
                #    print(f"Removing even pip: {not_reg_pip}")
                    print(f"Removing school pip: {school_pip}")
                    self.remove_pip(school_pip)
                else:
                    if use_power:
                        not_reg_pip = next((pip for pip in self.pips if pip.school != "REG"), None)
                        if not_reg_pip is not None:
                            print(f"removing not-reg pip: {not_reg_pip}")
                            self.remove_pip(not_reg_pip)
                            context.pips -= 2
                            continue

                    # there must be reg pips or else the spell should not cast
                    reg_pips = [pip for pip in self.pips if pip.school == "REG"]

                    for i, pip in enumerate(reg_pips):
                        if i >= 2:
                            break 
                        print(f"removing reg pip: {pip}")
                        self.remove_pip(pip)

                context.pips -= 2
                    
            # odd number means try to consume one reg pip
            # if no reg pip, then do pip conserve
            else:
                reg_pip = next((pip for pip in self.pips if pip.school == "REG"), None)
                if reg_pip:
                    self.remove_pip(reg_pip)
                else:
                    to_rem = self.pips[0]
                #   print(f"To remove pip: {to_rem}")
                    self.remove_pip(to_rem)
                #   conserved = True
                #    if conserved:
                #       caster_player.pips.insert(0, Pip("REG"))
                    #    print(f"After insertin reg: {caster_player.pips}")
                context.pips -= 1

            print(f"{context.pips} pips left to eat")
            print(f"Player has: {self.pips}")

        self.shadpips -= context.shadpips

        print(f"{self.name} has {self.pips} pips and {self.shadpips} shad pips after casting")


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