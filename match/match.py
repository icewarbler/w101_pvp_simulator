import json
import random
import math
import re
from .effects import Effect
from .effects import Single_Damage
from .effects import Trap
from .effects import Shield
from .effects import Charm
from .effects import Aura
from .effects import Ward
from .effects import Weakness
from .effects import DOT
from .effects import Heal_Weakness
from .effects import Bubble
from .player import Player
from .player import Deck
from .player import Hand
from .effects import Pip
from .spell_instance import SpellInstance

class Match:
    def __init__(self, p1, p2, turn, match_file=None):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn

        self.match_file = match_file

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
        print("doing damage...")
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
            if charm.type == "HEAL_WEAKNESS":
                continue
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

        if b:
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
        gambit_cause = gambit.cause[0]
        print(gambit_cause)
        # gambit_effect = gambit.per_effect

    #  print(json.dumps(gambit_cause, indent=4))
    #  print(json.dumps(gambit_effect, indent=4))

        effect_target = gambit_cause.get("TARGET")

        if effect_target == "SELF":
            abs_target = caster_player
        elif effect_target == "ENEMY":
            abs_target = enemy_player

        match gambit_cause.get("ACTION"):
            case "STEAL":
                effect_count = 0
                gambit_type = gambit_cause.get("TYPE")
                if gambit_type == "PIP":
                    reg_pip = next((pip for pip in enemy_player.pips if pip.school == "REG"), None)
                    if reg_pip:
                        enemy_player.remove_pip(reg_pip)
                    else:
                        to_rem = self.pips[0]
                    #   print(f"To remove pip: {to_rem}")
                        enemy_player.remove_pip(to_rem)
                        enemy_player.pips.insert(0, Pip("REG"))
                    effect_count += 1

                gambit_effect = gambit.per_effect

                per_effect_type = gambit_effect.get("TYPE")

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)
                
                for _ in range(effect_count):
                    if per_effect_type == "PIP":
                        print(f"Adding a pip???")
                        new_effect = effect_obj.clone()
                        reg_idx = caster_player.last_pip_index("REG")

                        if reg_idx is None:
                            caster_player.pips.insert(0, new_effect)
                        else:        
                            caster_player.pips.insert(reg_idx + 1, new_effect)

                        continue
            case "ECHO":
                effect_count = 0
               # gambit_type = gambit_cause.get("TYPE")
                for effect in abs_target.effects:
                    if effect.type == gambit_cause.get("TYPE"):
                        effect_count += 1
                        
                        if effect_count == gambit_cause.get("MAX"):
                            break

                print(f"amount: {effect_count}")

                gambit_effect = gambit.per_effect

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)

            #    per_effect_type = gambit_effect.get("TYPE")

                gambit_effect_target = gambit_effect["TARGET"]

                if gambit_effect_target == "SELF":
                    abs_target = caster_player
                elif gambit_effect_target == "ENEMY":
                    abs_target = enemy_player
                
                for _ in range(effect_count):
                    new_effect = effect_obj.clone()

                    if gambit_effect.get("TYPE") == "PIP":
                        reg_idx = caster_player.last_pip_index("REG")

                        if reg_idx is None:
                            caster_player.pips.insert(0, new_effect)
                        else:        
                            caster_player.pips.insert(reg_idx + 1, new_effect)

                        continue

                    abs_target.add_effect(new_effect)
                 #   hiii = Shield(per_effect_school, per_effect_value, per_effect_family)

                    print(f"Adding effect {new_effect} to {abs_target.name}")

                  #  self.add_effect(abs_target, hiii)

            case "SWAP":
                from_caster = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in caster_player.get_effects():
                    if effect.type == gambit_type:
                        from_caster.append(effect)
                        
                        if len(from_caster) == gambit_cause.get("MAX"):
                            break

                amount = len(from_caster)

                from_enemy = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in enemy_player.get_effects():
                    if effect.type == gambit_type:
                        from_enemy.append(effect)
                        
                        if len(from_enemy) == gambit_cause.get("MAX"):
                            break

                for effect in from_caster:
                    caster_player.del_effect(effect)

                    enemy_player.add_effect(effect)

                for effect in from_enemy:
                    enemy_player.del_effect(effect)

                    caster_player.add_effect(effect)

            case "DETONATE":
                to_explode = []
                gambit_type = gambit_cause.get("TYPE")

                for effect in abs_target.get_effects():
                    if effect.type == gambit_type:
                        to_explode.append(effect)
                        
                        if len(to_explode) == gambit_cause.get("MAX"):
                            break

                amount = len(to_explode)

                gambit_effect = gambit.per_effect

                for effect in to_explode:
                    multiplier = gambit_effect.get("VALUE")
                    abs_target.explode_dot(effect, multiplier)

            case "GAMBIT":
                to_remove = []
                gambit_type = gambit_cause.get("TYPE")

                cause_target = gambit_cause.get("TARGET")

                if cause_target == "SELF":
                    abs_target = caster_player
                elif cause_target == "ENEMY":
                    abs_target = enemy_player

                for effect in caster_player.get_effects():
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)

                for effect in to_remove:
                    abs_target.del_effect(effect)

                gambit_effect = gambit.per_effect

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
                for effect in abs_target.get_effects():
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)

                print(f"amount: {amount}")

                for effect in to_remove:
                    abs_target.del_effect(effect)

                gambit_effect = gambit.per_effect

                per_effect_type = gambit_effect.get("TYPE")

                gambit_effect = gambit.per_effect

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)

                if hasattr(effect_obj, "school"):
                    if effect_obj.school == "ENEMY_SCHOOL":
                        effect_obj.school = enemy_player.school
                    elif effect_obj.school == "ALLY_SCHOOL":
                        effect_obj.school = caster_player.school

                gambit_effect_target = gambit_effect["TARGET"]


                if gambit_effect_target == "SELF":
                    abs_target = caster_player
                elif gambit_effect_target == "ENEMY":
                    abs_target = enemy_player
                
                for _ in range(amount):
                    if per_effect_type == "PIP":
                        print(f"Adding a pip???")
                        new_effect = effect_obj.clone()
                        reg_idx = caster_player.last_pip_index("REG")

                        if reg_idx is None:
                            caster_player.pips.insert(0, new_effect)
                        else:        
                            caster_player.pips.insert(reg_idx + 1, new_effect)

                        continue
                    else:
                        new_effect = effect_obj.clone()

                        abs_target.add_effect(new_effect)

    def insert_starting_conditions(self):
        print(f"start name: {self.p1.name}")
        if self.p1.name == "EZRA POLARKNIGHT":
            p1 = self.p1 # ezra
            p2 = self.p2 # jason

            self.change_bubble(Bubble("FIRE", 25))

        #  print(f"{match_obj.global_effect}")

            p1.curr_health = 12887
            p2.curr_health = 9479

            p1.add_effect(Trap("FIRE", 65, None))
            adj = [{
                "TYPE": "SHIELD",
                "SCHOOL": "UNIVERSAL",
                "VALUE": 20
            }]
            p1.aura = Aura(2, adj)

            p2.add_effect(Trap("FIRE", 30, None))
            p2.add_effect(Trap("ICE", 30, None))
            p2.add_effect(Trap("STORM", 30, None))

            p1.pips.append(Pip("DEATH"))
            p1.pips.append(Pip("LIFE"))
            p1.pips.append(Pip("LIFE"))
            p1.pips.append(Pip("LIFE"))

            p1.shadpips = 1
            p2.shadpips = 2

            p2.pips.append(Pip("REG"))
            p2.pips.append(Pip("REG"))
            p2.pips.append(Pip("FIRE"))
            p2.pips.append(Pip("MYTH"))
            p2.pips.append(Pip("STORM"))

        if self.p1.name == "SUMI":
            p1 = self.p1 # sumi
            p2 = self.p2 # john

            p1.curr_health = 14610
            p2.curr_health = 13358

            p1.add_effect(Heal_Weakness(65, "INFECTION_65"))

            p1.add_effect(Weakness("ICE", 30, "ELEMENTALWEAKNESS_ICE30"))
            p1.add_effect(Weakness("STORM", 30, "ELEMENTALWEAKNESS_STORM30"))
            p1.add_effect(Weakness("FIRE", 30, "ELEMENTALWEAKNESS_FIRE30"))

            p2.add_effect(Weakness("UNIVERSAL", 35, None))

            p1.pips.append(Pip("REG"))
            p1.pips.append(Pip("BALANCE"))

            p2.pips.append(Pip("POWER"))
            p2.pips.append(Pip("POWER"))
            p2.pips.append(Pip("BALANCE"))
            p2.pips.append(Pip("FIRE"))

    def cast_spell(self, caster_player, enemy_player, spell_data):
        # if a player passes that turn, skip
        if spell_data in (None, "NONE"):
            return
        
        pipcost = spell_data.get("PIPCOST", 0)
        schoolpipcost = spell_data.get("SCHOOLPIPS", {})
        shadcost = spell_data.get("SHADCOST", 0)

        context = SpellInstance(spell_data, caster_player, enemy_player, pipcost, schoolpipcost, shadcost)

        print(f"{caster_player.name} pays {pipcost} pips, {schoolpipcost} school pips, and {shadcost} shad pips")

        caster_player.handle_pips(context)

        # loop through the effects of the spell
        # then apply them to the right player in match_obj
        for effect in context.spell["EFFECTS"]:
            effect_class = Effect.registry[effect["TYPE"]]
            effect_obj = effect_class.from_json(effect)
            print(f"Adding effect: {effect_obj}")

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

                    if effect_obj.type == "MINION":
                        abs_target.minion = effect_obj
                        continue

                    if effect_obj.type == "AURA":
                        abs_target.aura = effect_obj
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

                    amount = effect.get("AMOUNT", 1)

                    for _ in range(amount):
                        new_effect = effect_obj.clone()

                        if new_effect.type == "DOT":
                            new_effect.get_damage(self, caster_player, context)

                        abs_target.add_effect(new_effect)
                    
                case "MATCH":
                    self.global_effect = effect_obj

                case None:
                    effect_obj.apply(self, caster_player, enemy_player, context)

        for charm, player in context.charms_used.items():
            print(f"Used charm: {charm}")
            player.del_effect(charm)

    def minion_turn(self, caster_player, enemy_player, minion, minion_spell):
        print(f"min dur: {minion.duration}")
        if minion.duration == 7: 
            return
        
        minion_spell = minion.cast_spell(minion_spell)
        print(f"**Minion casts spell {minion_spell.get("SPELL")}")

        for effect in minion_spell.get("EFFECTS"):
            effect_class = Effect.registry[effect["TYPE"]]
            effect_obj = effect_class.from_json(effect)

            effect_target = effect.get("TARGET")
            if effect_target == "ALLY":
                if hasattr(effect_obj, "school"):
                    if effect_obj.school == "ALLY_SCHOOL":
                        effect_obj.school = caster_player.school

                print(f"Adding effect {effect_obj} to {caster_player.name}!")

                amount = effect.get("AMOUNT", 1)
                for _ in range(amount):
                    new_effect = effect_obj.clone()

                    caster_player.add_effect(new_effect)
            else:
                if enemy_player.minion:
                    target = random.randrange(0,2)
                    if target == 0:
                        enemy_player.add_effect(effect)
                    else:
                        enemy_player.minion.add_effect(effect)
                else:
                    print(f"Adding effect {effect_obj} to {enemy_player.name}!")
                    enemy_player.add_effect(effect_obj)

    def load_json(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("ERROR! FAILED TO DECODE JSON!")

    def init_match(self):
        self.p1.pips.append(Pip("REG"))
        self.p1.pips.append(Pip("POWER"))
        self.p1.pips.append(Pip("POWER"))

        self.p1.shadpips = 1
        self.p2.shadpips = 2

        self.p2.pips.append(Pip("REG"))
        self.p2.pips.append(Pip("POWER"))
        self.p2.pips.append(Pip("POWER"))

    def parse_input(self, spell_lookup, caster_player, enemy_player):
        selection = input("> ").strip().lower()

        if selection == "info":
            print("OPTIONS:")
            print(f"[1-7] - Choose a spell to cast")
            print(f"d[1-7] - Delete a spell from your hand")
            print(f"i[1-7] - Print out the info for a spell")
            print(f"cs - Change the selected archmastery pip")
            print(f"ss - Print the currently selected archmastery pip")
            print(f"ee - Print the enemy's current effects")
            print(f"me - Print your current effects")
            print(f"health - Print the current health of both you and the enemy")
            print(f"pips - Print out your current pips")
            return 0

        if selection in ("p", "pass"):
            spell_id = None
            return spell_id

        if re.match(r'^d[1-7]$', selection):
            print(f"selection: {selection}")
            if 1 <= int(selection[1:]) <= len(caster_player.hand.cards):
                spell_id = caster_player.hand.cards[int(selection[1:]) - 1]
                print(spell_id)
                caster_player.delete_card(spell_id)
                return 0

        if re.match(r'^i[1-7]$', selection):
            print(f"selection: {selection}")
            if 1 <= int(selection[1:]) <= len(caster_player.hand.cards):
                spell_id = caster_player.hand.cards[int(selection[1:]) - 1]
                print(spell_id)
                spell_data = spell_lookup.get(spell_id)
                print(f"{spell_data.get("DESCRIPTION")}")
                return 0

        if selection == "health":
            print(f"Your Health: {caster_player.curr_health}")
            print(f"Enemy Health: {enemy_player.curr_health}")
            return 0

        if selection == "pips":
            print(f"Your pips: {caster_player.pips}")
            return 0
        
        if selection == "ee":
            if enemy_player.aura:
                print(enemy_player.aura)
            if enemy_player.backlash:
                print(enemy_player.backlash)
            print(enemy_player.print_effects())

        if selection == "me":
            if caster_player.aura:
                print(caster_player.aura)
            if caster_player.backlash:
                print(caster_player.backlash)
            print(caster_player.print_effects())
        
        if selection == "cs":
            schools = [
                "FIRE",
                "ICE",
                "STORM",
                "LIFE",
                "DEATH",
                "MYTH",
                "BALANCE"
            ]

            print("Generate which archmastery pip?")

            for i, school in enumerate(schools):
                print(f"{i + 1}. {school}")

            while True:
                try:
                    school_selection = int(input("> "))
                except ValueError:
                    continue

                if 1 <= school_selection <= len(schools):
                    break

            caster_player.selected_school = schools[school_selection - 1]

        if selection == "ss":
            print(f"Currently generating a {caster_player.selected_school} pip")
        
        try:
            selection = int(selection)
        except ValueError:
            print("Enter a card number or pass.")
            return 0

        if 1 <= selection <= len(caster_player.hand.cards):
            spell_id = caster_player.hand.cards[selection - 1]
            return spell_id

    def start_match(self):
        if not self.match_file:
            turn = 0

            self.p1.deck = Deck(self.p1.deck)
            print(f"{self.p1.name} DECK:")
            print(self.p1.deck)
            print("----")


            for _ in range(Hand.max_cards):
                self.p1.draw_card()

            self.p2.deck = Deck(self.p2.deck)
            print(f"{self.p2.name} DECK:")
            print(self.p2.deck)
            print("----")

            for _ in range(Hand.max_cards):
                self.p2.draw_card()

            spells = self.load_json("json_data/spells.json")

            spell_lookup = { spell["ID"]: spell for spell in spells }
            print(len(spell_lookup))

            self.init_match()

            # loop to do turn
            while True:
                if turn % 2 == 0:
                    caster_player = self.p1
                    enemy_player = self.p2
                else:
                    caster_player = self.p2
                    enemy_player = self.p1

                while len(caster_player.hand.cards) < Hand.max_cards and len(caster_player.deck.cards):
                 #   print(f"{caster_player.name} has {len(caster_player.hand.cards)} cards in hand!")
                    caster_player.draw_card()
                
                # print(f"{caster_player.name} HAND:")
                # print(caster_player.hand)

                # for i, card in enumerate(caster_player.hand.cards):
                #     print(f"{i + 1}. {card}")

                print(f"{caster_player.name} HEALTH: {caster_player.curr_health} / {caster_player.max_health}")
                print(f"{enemy_player.name} HEALTH: {enemy_player.curr_health} / {enemy_player.max_health}")

                print(f"Your pips: {caster_player.pips}")

                # loop to select a spell
                while True:
                    red = "\033[91m"
                    reset = "\033[0m"
                    for i, card in enumerate(caster_player.hand.cards):
                        spell = spell_lookup[card]

                        if caster_player.can_cast(spell):
                            print(f"{i + 1}. {card}")
                        else:
                            print(f"{i + 1}. {red}{card}{reset}")

                    spell_id = self.parse_input(spell_lookup, caster_player, enemy_player)
                    spell_data = spell_lookup.get(spell_id)
                    if spell_id != 0 and caster_player.can_cast(spell_data):
                        break

                # if a player passes that turn, skip
                if spell_id in (None, "NONE"):
                    print(f"**PASS")
                    print(f"Round {turn}: {caster_player.name} PASSES")

                if spell_id not in (None, "NONE"):
                    print(f"**SPELL: {spell_id}")
                    # get data from that spell to add to match
                    spell_data = spell_lookup.get(spell_id)

                    print(f"Round {turn}: {caster_player.name} casts {spell_id}")

                    self.cast_spell(caster_player, enemy_player, spell_data)

                    caster_player.delete_card(spell_id)

                for effect in caster_player.effects:
                    effect.end_round()

                if caster_player.curr_health <= 0 or enemy_player.curr_health <= 0:
                    self.end_match(caster_player, enemy_player)
                    break

                # pip conservation stuff
                # pip conservation means that for a spell that requires odd pips
                # using up a power pip leaves behind a regular pip
                conserved = True
                
                if conserved:
                    caster_player.pips.insert(0, Pip("REG"))

                # places the pip after all the regular pips
                reg_idx = caster_player.last_pip_index("REG")

                if reg_idx is None:
                    caster_player.pips.insert(0, Pip(caster_player.selected_school))
                else:        
                    caster_player.pips.insert(reg_idx + 1, Pip(caster_player.selected_school))

                turn += 1
            return

        if self.match_file:
            match_dat = self.load_json(self.match_file)
        spells = self.load_json("json_data/spells.json")

        self.insert_starting_conditions()

        spell_lookup = { spell["ID"]: spell for spell in spells }

        print(f"P1 HEALTH: {self.p1.curr_health}")
        print(f"P2 HEALTH: {self.p2.curr_health}")

        for turn in match_dat:
            round = turn["ROUND"]
            # if round > 18:
            #     break
            caster = turn["CASTER"]

            if caster == "PLAYER1":
                caster_player = self.p1
                enemy_player = self.p2
            elif caster == "PLAYER2":
                caster_player = self.p2
                enemy_player = self.p1

            print("----")

            # this is where backlash is taken
            if caster_player.backlash:
                caster_player.take_backlash()

            # this is where backlash eats
            print(f"caster_backlash: {caster_player.backlash}")
            if caster_player.backlash:
                caster_player.backlash_eat(enemy_player)

            # this is where DOTs activate
            caster_player.activate_dots(self)

            caster_player.activate_bombs()

            self.p1.print_effects()
            self.p2.print_effects()

            # gets the spell name cast on that turn from w101_ezra_jason.json
            spell_name = turn["SPELL"]

            # if a player passes that turn, skip
            if spell_name in (None, "NONE"):
                print(f"**PASS")
                print(f"Round {round}: {caster_player.name} PASSES")

            if spell_name not in (None, "NONE"):
                print(f"**SPELL: {spell_name}")
                # get data from that spell to add to match
                spell_data = spell_lookup.get(spell_name)

                print(f"Round {round}: {caster_player.name} casts {spell_name}")

                self.cast_spell(caster_player, enemy_player, spell_data)

            # checks if a player has reached 0 health (end match)
            if caster_player.curr_health <= 0 or enemy_player.curr_health <= 0:
                self.end_match(caster_player, enemy_player)
                break

            if caster == "PLAYER1":
                for effect in self.p1.effects:
                    effect.end_round()
            else:
                for effect in self.p2.effects:
                    effect.end_round()

            if caster_player.aura is not None:
                caster_player.aura.end_round()
                print("Caster aura:")
                print(caster_player.aura)
                if caster_player.aura.expired():
                    caster_player.aura = None
            
            if enemy_player.aura is not None:
                print("Enemy aura:")
                print(enemy_player.aura)

            if caster_player.backlash is not None:
                caster_player.backlash.end_round()

            if caster_player.minion:
                print(f"doing minion turn...")
                self.minion_turn(caster_player, enemy_player, caster_player.minion, turn.get("MINION_CAST"))
                caster_player.minion.duration -= 1

            self.p1.print_effects()
            self.p2.print_effects()

            # pip conservation stuff
            # pip conservation means that for a spell that requires odd pips
            # using up a power pip leaves behind a regular pip
            if turn.get("CONSERVE_PIP") in (None, "NONE"):
                conserved = None
            else:
                conserved = turn["CONSERVE_PIP"]
            
            if conserved:
                caster_player.pips.insert(0, Pip("REG"))

            # archmastery stuff
            school_pip = turn.get("SELECTED_SCHOOL")

            # places the pip after all the regular pips
            reg_idx = caster_player.last_pip_index("REG")

            if reg_idx is None:
                caster_player.pips.insert(0, Pip(school_pip))
            else:        
                caster_player.pips.insert(reg_idx + 1, Pip(school_pip))

            caster_player.sort_pips()
            print(caster_player.pips)

            if turn.get("GAIN_SHAD") == True:
                caster_player.shadpips += 1

            print(f"{caster_player.name} has {caster_player.shadpips} shadpips")


    def end_match(self, caster_player, enemy_player):
        if caster_player.curr_health <= 0:
            print(f"{caster_player.name} has been defeated!")
        elif enemy_player.curr_health <= 0:
            print(f"{enemy_player.name} has been defeated!")