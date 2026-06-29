import json
import pandas as pd
import random
from w101_effects import Effect
from w101_effects import Single_Damage
from w101_effects import Trap
from w101_effects import Charm
from w101_effects import Aura
from w101_effects import Ward
from w101_effects import Weakness
from w101_player import Player

class Match:
    def __init__(self, p1, p2, turn):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn
        self.global_effect = []

        self.current_instance = None

    def getPlayer1(self):
        return self.p1
    
    def getPlayer2(self):
        return self.p2
    
    def getBubble(self):
        return self.global_effect
    
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

    def change_bubble(self, bubble):
        self.global_effect = bubble

    # def consume_instance(spell_instance):
    #     for charm in spell_instance.charms_used:
    #         pass
    #     for ward in spell_instance.wards_used:
    #         pass
                
    # have to store caster pierce as well as this damage
    # bubble and enemy stats are added when the dot is activated
    # this function is called when dot is cast
    # other stat function is called at begin of turn
    def dot_outgoing_damage(self, caster_player, enemy_player, effect):
        effect_target = effect["TARGET"]
        if effect_target == "SELF":
            abs_target = caster_player
        elif effect_target == "ENEMY":
            abs_target = enemy_player

        effect_school = effect["SCHOOL"]

        effect_value = effect["VALUE"]

        print(f"Effect val: {effect_value}")

        # gets caster's outgoing damage
        print(caster_player.get_outgoing_damage(effect_school))
    # print(f"value: {effect_value}")
        effect_value += (effect_value * caster_player.get_outgoing_damage(effect_school) * 0.01)
    #  print(f"a1: {effect_value}")

        # gets caster's aura
        if caster_player.aura is not None:
            print("inside")
            # do stuff

        # gets any blades/weaknesses caster may have
        caster_charms = [ effect for effect in caster_player.effects if isinstance(effect, Charm) ]

        used_charm_families = set()

        for charm in caster_charms:
            if charm.school in (effect_school, "UNIVERSAL"):
                if charm.family in used_charm_families:
                    continue
                used_charm_families.add(charm.family)
                print(f"Charm used: {charm.school} of val {charm.value}")
                effect_value = charm.mod_damage(effect_value)
                caster_player.del_effect(charm)

    def do_damage(self, caster_player, enemy_player, effect):
        effect_target = effect["TARGET"]
        if effect_target == "SELF":
            abs_target = caster_player
        elif effect_target == "ENEMY":
            abs_target = enemy_player

        effect_school = effect["SCHOOL"]

        if effect["TYPE"] == "SINGLE_DAMAGE":
            effect_value = effect["VALUE"]
        elif effect["TYPE"] == "RANGE_DAMAGE":
            effect_value = random.randrange(effect["MIN"], effect["MAX"], 5)
        
        print(f"Effect val: {effect_value}")


        # the order for activating damage is:
        # caster gear (% then flat) -> 
        # caster aura -> 
        # caster charms-> 
        # the global -> 
        # target's aura ->
        # target's wards -> 
        # target's gear (flat then %) -> 
        # critical 

    # print(caster_player.name)
    # print(f"default dmg: {effect_value}")

        print(f"caster pierce: {caster_player.pierce[effect_school]} {effect_school}") 

        # gets caster's outgoing damage
        print(caster_player.get_outgoing_damage(effect_school))
    # print(f"value: {effect_value}")
        effect_value += (effect_value * caster_player.get_outgoing_damage(effect_school) * 0.01)
    #  print(f"a1: {effect_value}")

        # gets caster's aura
        if caster_player.aura is not None:
            print("inside")
            # do stuff

        # gets any blades/weaknesses caster may have
        caster_charms = [ effect for effect in caster_player.effects if isinstance(effect, Charm) ]

        used_charm_families = set()

        for charm in caster_charms:
            if charm.school in (effect_school, "UNIVERSAL"):
                if charm.family in used_charm_families:
                    continue
                used_charm_families.add(charm.family)
                print(f"Charm used: {charm.school} of val {charm.value}")
                effect_value = charm.mod_damage(effect_value)
                caster_player.del_effect(charm)

        # if Charm in caster_player.get_effects():
        #     print("blade")
        #     # do stuff

        # gets the global
        b = self.getBubble()

        if b.school == effect_school:
        #  print(f"Found bubble with value {b.value}")
            effect_value += effect_value * b.value * 0.01
        
    #  print(f"post-bubble effect_value: {effect_value}")

        # gets any auras the enemy may have
       # enemy_aura = next( (effect for effect in abs_target.effects if isinstance(effect, Aura)), None )
        if abs_target.aura is not None:
            adj = abs_target.aura.adj

            print(json.dumps(adj, indent=4))

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (effect_school, "UNIVERSAL"):
                    # ignore if not shield/trap type aura
                    if modifier["TYPE"] == "SHIELD":
                        effect_value -= effect_value * modifier["VALUE"] * 0.01
                    elif modifier["TYPE"] == "TRAP":
                        effect_value += effect_value * modifier["VALUE"] * 0.01

    #  print(f"post-aura effect_value: {effect_value}")


        # gets enemy shields/traps
        enemy_wards = [ effect for effect in abs_target.effects if isinstance(effect, Ward) ]

        used_families = set()

        for ward in enemy_wards:
            if ward.school in (effect_school, "UNIVERSAL"):
                if ward.family in used_families:
                    continue
                if ward.type == "DOT_TRAP":
                    continue
                used_families.add(ward.family)
                print(f"Ward used: {ward.school} of val {ward.value}")
                effect_value = ward.mod_damage(effect_value)
                abs_target.del_effect(ward)
        
    #  print(f"Post-ward effect_value: {effect_value}")

        # gets enemy resist
        enemy_res = abs_target.get_incoming_resist(effect_school)
        print(f"enemy res: {enemy_res}")
        effect_value -= effect_value * enemy_res * 0.01
    #  print(f"Post-resist effect_value: {effect_value}")

        abs_target.dec_health(effect_value)
        print(f"Does {effect_value} damage!")
        print(f"{abs_target.name} HEALTH: {abs_target.curr_health}")

    def play_gambit(self, caster_player, enemy_player, effect):
        gambit_cause = effect.cause
        print(gambit_cause)
        gambit_effect = effect.per_effect

    #  print(json.dumps(gambit_cause, indent=4))
    #  print(json.dumps(gambit_effect, indent=4))

        effect_target = gambit_cause.get("TARGET")

        if effect_target == "SELF":
            abs_target = caster_player
        elif effect_target == "ENEMY":
            abs_target = enemy_player

        match gambit_cause.get("ACTION"):
            case "GAMBIT":
                to_remove = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in caster_player.get_effects():
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)

                for effect in to_remove:
                    abs_target.del_effect(effect)

                per_effect_type = gambit_effect.get("TYPE")
                
                for _ in range(amount):
                    if per_effect_type == "HEAL_WEAKNESS":
                        gambit_effect_target = gambit_effect["TARGET"]

                        if gambit_effect_target == "SELF":
                            abs_target = caster_player
                        elif gambit_effect_target == "ENEMY":
                            abs_target = enemy_player

                        per_effect_value = gambit_effect.get("VALUE")
                        per_effect_family = gambit_effect.get("FAMILY")

                        hiii = Weakness(per_effect_value, per_effect_family)

                        self.add_effect(abs_target, hiii)

            case "CLEAR":
                to_remove = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in caster_player.get_effects():
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)


                for effect in to_remove:
                    abs_target.del_effect(effect)

                per_effect_type = gambit_effect.get("TYPE")
                
                for _ in range(amount):
                    if per_effect_type == "TRAP":
                        gambit_effect_target = gambit_effect["TARGET"]

                        if gambit_effect_target == "SELF":
                            abs_target = caster_player
                        elif gambit_effect_target == "ENEMY":
                            abs_target = enemy_player

                        per_effect_school = gambit_effect.get("SCHOOL")
                        per_effect_value = gambit_effect.get("VALUE")
                        per_effect_family = gambit_effect.get("FAMILY")

                        if per_effect_school == "TARGET_SCHOOL":
                            per_effect_school = abs_target.school

                        jel = Trap(per_effect_school, per_effect_value, per_effect_family)

                        self.add_effect(abs_target, jel)


    # def get_p1_effects(self):
    #     return self.p1e
    
    # def get_p2_effects(self):
    #     return self.p2e

    # def delete_effect(self, target):
    #     if target == "p1":

