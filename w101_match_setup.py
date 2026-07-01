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
from w101_effects import DOT
from w101_player import Player

class Match:
    def __init__(self, p1, p2, turn):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn
        self.global_effect = []

    def getPlayer1(self):
        return self.p1
    
    def getPlayer2(self):
        return self.p2
    
    def getBubble(self):
        return self.global_effect

    def add_effect(self, target_obj, effect):

        # effect = Effect(
        #     effect_type = spell_effects.get("")
        #     value = spell.effects.ward.value
        # )
        target_obj.add_effect(effect)

    def change_bubble(self, bubble):
        self.global_effect = bubble
                
    # have to store caster pierce as well as this damage
    # bubble and enemy stats are added when the dot is activated
    # this function is called when dot is cast
    # other stat function is called at begin of turn
    def dot_damage(self, caster_player, effect, context):
        effect_school = effect.school

        effect_value = effect.value

        print(f"Base effect val: {effect_value}")

        # gets caster's outgoing damage
        print(caster_player.get_outgoing_damage(effect_school))
    # print(f"value: {effect_value}")
        effect_value += (effect_value * caster_player.get_outgoing_damage(effect_school) * 0.01)
    #  print(f"a1: {effect_value}")

        print(f"with damage: {effect_value}")

        caster_pierce = caster_player.pierce[effect_school]
        effect.pierce_val = caster_pierce

        print(f"pierce_val: {effect.pierce_val} {effect_school}") 

        # gets caster's aura
        if caster_player.aura is not None:
            adj = caster_player.aura.adj

         #   print(json.dumps(adj, indent=4))

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (effect_school, "UNIVERSAL"):
                    # ignore if not blade/weakness type aura
                    if modifier["TYPE"] == "WEAKNESS":
                        effect_value -= effect_value * modifier["VALUE"] * 0.01
                    elif modifier["TYPE"] == "BLADE":
                        effect_value += effect_value * modifier["VALUE"] * 0.01

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
                if charm not in context.charms_used:
                    context.add_used_charm(caster_player, charm)
            #    caster_player.del_effect(charm)

        # gets the global
        b = self.global_effect

        if b.school == effect_school:
            print(f"Found bubble with value {b.value}")
            effect_value += effect_value * b.value * 0.01

        print(f"DOT value: {effect_value}")
        effect.new_damage(effect_value)

        tick_damage = effect_value / effect.duration
        effect.new_tick_damage(tick_damage)
        print(f"tick dmg: {effect.value_per_tick}")

    def do_tick(self, caster, dot):
        effect_value = dot.value_per_tick
        pierce_val = dot.pierce_val
        # gets any auras the enemy may have
       # enemy_aura = next( (effect for effect in abs_target.effects if isinstance(effect, Aura)), None )
        if caster.aura is not None:
            adj = caster.aura.adj

        #    print(json.dumps(adj, indent=4))

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (dot.school, "UNIVERSAL"):
                    print(json.dumps(modifier, indent=4))
                    # ignore if not shield/trap type aura
                    if modifier["TYPE"] == "SHIELD":
                        mod_val = modifier["VALUE"]
                        print(f"mod_val: {mod_val}; pierce_val: {pierce_val}")
                        mod_val -= pierce_val
                        if mod_val < 0:
                            pierce_val = -(mod_val)
                            print(f"pierce_val: {pierce_val}; mod_val: {mod_val}")
                            mod_val = 0
                        effect_value -= effect_value * mod_val * 0.01
                    elif modifier["TYPE"] == "TRAP":
                        effect_value += effect_value * modifier["VALUE"] * 0.01

    #  print(f"post-aura effect_value: {effect_value}")


        # gets enemy shields/traps
        enemy_wards = [ effect for effect in caster.effects if isinstance(effect, Ward) ]

        used_families = set()

        for ward in enemy_wards:
            if ward.school in (dot.school, "UNIVERSAL"):
                if ward.family in used_families:
                    continue
                used_families.add(ward.family)
                print(f"Ward used: {ward.school} of val {ward.value}")
                pierce_val, effect_value = ward.mod_damage(effect_value, pierce_val)
                print(f"post-ward effect_value: {effect_value}; pierce_val: {pierce_val}")
                caster.del_effect(ward)
        
    #  print(f"Post-ward effect_value: {effect_value}")

        # gets enemy resist
        enemy_res = caster.get_incoming_resist(dot.school)
        print(f"init enemy res: {enemy_res}")
        enemy_res -= pierce_val
        print(f"enemy res: {enemy_res}; pierce_val: {pierce_val}")
        enemy_res = 0 if enemy_res < 0 else enemy_res
        effect_value -= effect_value * enemy_res * 0.01
    #  print(f"Post-resist effect_value: {effect_value}")

        caster.dec_health(effect_value)
        print(f"DOT tick does {effect_value} damage!")
        print(f"{caster.name} HEALTH: {caster.curr_health}")


    def do_damage(self, caster_player, enemy_player, effect, context):
        if effect.target == "SELF":
            abs_target = caster_player
        elif effect.target == "ENEMY":
            abs_target = enemy_player

        effect_school = effect.school

        if effect.type == "SINGLE_DAMAGE":
            effect_value = effect.value
        elif effect.type == "RANGE_DAMAGE":
            effect_value = random.randrange(effect.min, effect.max, 5)
        
        print(f"Base effect val: {effect_value}")


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

        pierce_val = caster_player.pierce[effect_school]

        print(f"caster pierce: {pierce_val} {effect_school}") 

        # gets caster's outgoing damage
        print(caster_player.get_outgoing_damage(effect_school))
    # print(f"value: {effect_value}")
        effect_value += (effect_value * caster_player.get_outgoing_damage(effect_school) * 0.01)
    #  print(f"a1: {effect_value}")

        # gets caster's aura
        # gets caster's aura
        if caster_player.aura is not None:
            adj = caster_player.aura.adj

           # print(json.dumps(adj, indent=4))

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (effect_school, "UNIVERSAL"):
                    print(json.dumps(modifier, indent=4))
                    # ignore if not blade/weakness type aura
                    if modifier["TYPE"] == "WEAKNESS":
                        effect_value -= effect_value * modifier["VALUE"] * 0.01
                    elif modifier["TYPE"] == "BLADE":
                        effect_value += effect_value * modifier["VALUE"] * 0.01

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
                context.add_used_charm(caster_player, charm)
            #    caster_player.del_effect(charm)

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

        #    print(json.dumps(adj, indent=4))

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (effect_school, "UNIVERSAL"):
                    print(json.dumps(modifier, indent=4))
                    # ignore if not shield/trap type aura
                    if modifier["TYPE"] == "SHIELD":
                        mod_val = modifier["VALUE"]
                        print(f"mod_val: {mod_val}; pierce_val: {pierce_val}")
                        mod_val -= pierce_val
                        if mod_val < 0:
                            pierce_val = -(mod_val)
                            print(f"pierce_val: {pierce_val}; mod_val: {mod_val}")
                            mod_val = 0
                        effect_value -= effect_value * mod_val * 0.01
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
                print(f"{ward.type} used: {ward.school} of val {ward.value}")
                pierce_val, effect_value = ward.mod_damage(effect_value, pierce_val)
                print(f"post-ward effect_value: {effect_value}; pierce_val: {pierce_val}")
             #   context.add_used_ward(abs_target, ward)
                abs_target.del_effect(ward)
        
    #  print(f"Post-ward effect_value: {effect_value}")

        # gets enemy resist
        enemy_res = abs_target.get_incoming_resist(effect_school)
        print(f"init enemy res: {enemy_res}")
        enemy_res -= pierce_val
        print(f"enemy res: {enemy_res}; pierce_val: {pierce_val}")
        enemy_res = 0 if enemy_res < 0 else enemy_res
        effect_value -= effect_value * enemy_res * 0.01
    #  print(f"Post-resist effect_value: {effect_value}")

        abs_target.dec_health(effect_value)
        print(f"Does {effect_value} damage!")
        print(f"{abs_target.name} HEALTH: {abs_target.curr_health}")

    def play_gambit(self, caster_player, enemy_player, gambit, context):
        gambit_cause = gambit.cause
        print(gambit_cause)
        gambit_effect = gambit.per_effect

    #  print(json.dumps(gambit_cause, indent=4))
    #  print(json.dumps(gambit_effect, indent=4))

        effect_target = gambit_cause.get("TARGET")

        if effect_target == "SELF":
            abs_target = caster_player
        elif effect_target == "ENEMY":
            abs_target = enemy_player

        match gambit_cause.get("ACTION"):
            case "DETONATE":
                to_explode = []
                gambit_type = gambit_cause.get("TYPE")

                for effect in abs_target.get_effects():
                    if effect.type == gambit_type:
                        to_explode.append(effect)
                        
                        if len(to_explode) == gambit_cause.get("MAX"):
                            break

                amount = len(to_explode)

                for effect in to_explode:
                    multiplier = gambit_effect.get("VALUE")
                    abs_target.explode_dot(effect, multiplier)

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
                    if per_effect_type == "PIP":
                        print(f"Adding a pip???")
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

    def end_match(self, caster_player, enemy_player):
        if caster_player.curr_health <= 0:
            print(f"{caster_player.name} has been defeated!")
        elif enemy_player.curr_health <= 0:
            print(f"{enemy_player.name} has been defeated!")