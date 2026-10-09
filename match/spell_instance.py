# This holds an instance of the current spell
# Used right now to hold charms for multiple damage effects in a single spell
# (wards do not need to be held)
from random import random
import math
from .effects import Effect, Pip
from .action import Action
from .dataloader import load_json

class SpellInstance:
    def __init__(self, match, spell, caster, enemy, pips, schoolpips, shadpips, multi=False):
        self.spell = spell
        
        self.caster = caster
        self.enemy = enemy
        self.match = match

        self.charms_used = {}
        self.pips = pips 
        self.schoolpips = schoolpips
        self.shadpips = shadpips
        if self.shadpips is None:
            self.shadpips = 0

        self.multi = multi

    def add_used_charm(self, player, charm):
        self.charms_used[charm] = player

    def calc_pipcost(self):
        pipcost = self.pips
        
        school_pipcost = self.schoolpips
        print(f"pipcs: {pipcost}, spc: {school_pipcost}")

        for key, item in school_pipcost.items() if school_pipcost else []:
            print(f"{key}: {item}")
            pipcost += int(item*2)
            print(f"pipc new: {pipcost}")

        return pipcost

    # calculates the value of the spell based on damage per pip
    def spell_value(self):
        # calculate the value of each spell
        # this is determined by the effects on the field, the school
        # of the players, and the value of each spell effect, per pip

        # damage is divided by the number of pips
        spell_pipcost = self.calc_pipcost()
        # if pipcost > max_pipcost:
        #     max_pipcost = pipcost
        #     selected_spell = self.spell
        value = spell_pipcost

        types = self.spell.get("TYPE")
        print(f"type: {types}")

        if "DAMAGE" in types:
            effects = self.spell.get("EFFECTS")
            
            total_damage = 0

            for effect in effects:
                if effect.get("TYPE") == "SINGLE_DAMAGE":
                    damage_value = effect.get("VALUE")
                    total_damage += damage_value

            print(f"damage: {total_damage}")

            # calculate the value of the spell based on the damage and pip cost
            value += total_damage / spell_pipcost
            print(f"value: {value}")

        return value

    def cast_spell(self, caster_player, enemy_player):
        print(f"{caster_player.name} pays {self.pips} pips, {self.schoolpips} school pips, and {self.shadpips} shad pips")

        caster_player.handle_pips(self)

        # loop through the effects of the spell
        # then apply them to the right player in match_obj
        for effect in self.spell["EFFECTS"]:
            if effect["TYPE"] == "MINION":
                minions = load_json("json_data/minions.json")
                minion_lookup = { minion["ID"]: minion for minion in minions }
                minion_data = minion_lookup.get(effect["ID"])
                effect_class = Effect.registry[effect["TYPE"]]
                effect_obj = effect_class.from_json(minion_data)
            else: 
                effect_class = Effect.registry[effect["TYPE"]]
                effect_obj = effect_class.from_json(effect)
            print(f"Adding effect: {effect_obj}")

            effect_target = effect.get("TARGET")
            
            if effect_target == "SELF":
                abs_target = caster_player
            elif effect_target == "ENEMY":
                abs_target = enemy_player

            # if chromatic, set desired school
            if hasattr(effect_obj, "school"):
                if effect_obj.school == "ENEMY_SCHOOL":
                    effect_obj.school = enemy_player.school
                elif effect_obj.school == "ALLY_SCHOOL":
                    effect_obj.school = caster_player.school
                elif effect_obj.school == "SECONDARY_SCHOOL":
                    effect_obj.school = abs_target.secondary_school

            match effect_obj.store_at():
                case "PLAYER":
                    effect_target = effect["TARGET"]

                    if effect_target == "SELF":
                        abs_target = caster_player
                    elif effect_target == "ENEMY":
                        abs_target = enemy_player

                    if hasattr(effect_obj, "school"):
                        if effect_obj.school == "ENEMY_SCHOOL":
                            effect_obj.school = enemy_player.school
                        elif effect_obj.school == "ALLY_SCHOOL":
                            effect_obj.school = caster_player.school
                        elif effect_obj.school == "SECONDARY_SCHOOL":
                            effect_obj.school = abs_target.secondary_school

                    if effect_obj.type == "MINION":
                        abs_target.minion = effect_obj
                        abs_target.minion.pips.append(Pip("REG"))
                        continue

                    if effect_obj.type == "AURA":
                        abs_target.aura = effect_obj
                        # -1 if negative aura; +1 if positive aura
                        continue

                    if effect_obj.type == "BACKLASH":
                        if abs_target.backlash is not None:
                            perc_dmg = caster_player.backlash.accumulated
                            dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
                            print(f"{caster_player.name} takes {dmg_taken} damage!")
                            caster_player.dec_health(dmg_taken)
                            print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
                        abs_target.backlash = effect_obj
                        continue

                    if effect_obj.type == "PIP":
                        print(f"Adding effect: {effect_obj}")
                        abs_target.pips.append(Pip(effect_obj.school))
                        continue

                    amount = effect.get("AMOUNT", 1)

                    for _ in range(amount):
                        new_effect = effect_obj.clone()

                        if new_effect.type == "DOT":
                            new_effect.get_damage(self.match, caster_player, self)

                        abs_target.add_effect(new_effect)
                    
                case "MATCH":
                    self.global_effect = effect_obj

                case None:
                    action = Action(effect_obj, caster_player, enemy_player, self.match, self)
                    if "DAMAGE" in effect_obj.categories and self.multi:
                        # put code here to determine how many user selected
                        effect_obj.value = effect_obj.value / 2
                        effect_obj.apply(self, caster_player, enemy_player.minion, self.match, self)
                    effect_obj.apply(action)

        for charm, player in self.charms_used.items():
            print(f"Removing charm: {charm}")
            player.del_effect(charm)