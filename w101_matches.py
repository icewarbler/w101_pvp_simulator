import json
import pandas as pd
import math
from w101_effects import Effect
from w101_effects import Damage
from w101_effects import Charm
from w101_effects import Ward
from w101_effects import Trap
from w101_effects import Shield
from w101_effects import Backlash
from w101_effects import Aura
from w101_effects import Bubble
from w101_player import Player
from w101_match_setup import Match

def print_turn_info(round, caster_player, spell_name):
    print(f"Round {round}: {caster_player.name} casts {spell_name}")

def print_effects(player):
    print(f"{player.name}:")
    for effect in player.effects:
        print(f"{effect}")

def get_target(caster_player, enemy_player, effect):
    effect_target = effect.get("TARGET")

    if effect_target == "SELF":
        target = caster_player
    elif effect_target == "ENEMY":
        target = enemy_player
    return target

def insert_starting_conditions(match_obj):
    p1 = match_obj.getPlayer1() # ezra
    p2 = match_obj.getPlayer2() # jason

    match_obj.change_bubble(Bubble("FIRE", 25))

  #  print(f"{match_obj.global_effect}")

    p1.add_effect(Trap("FIRE", 65, None))
    adj = {
        "TYPE": "SHIELD",
        "SUBTYPE": "DAMAGE",
        "SCHOOL": "UNIVERSAL",
        "VALUE": 25
    }
    p1.add_effect(Aura(2, adj))

    p2.add_effect(Trap("FIRE", 30, None))
    p2.add_effect(Trap("ICE", 30, None))
    p2.add_effect(Trap("STORM", 30, None))

# fire ice storm (traps/shields) -> put on order
# ice storm fire (blades) -> put on order
# cleanse charm removes fire weakness - ice/storm left
# pierce removes storm shield - fire/ice left
def do_damage(match_obj, caster_player, enemy_player, effect):
    abs_target = get_target(caster_player, enemy_player, effect)

    effect_school = effect.get("SCHOOL")
    effect_value = effect.get("VALUE")

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

   # print(f"caster pierce: {caster_player.pierce[effect_school]} {effect_school}") 

    # gets caster's outgoing damage
  #  print(caster_player.get_outgoing_damage(effect_school))
   # print(f"value: {effect_value}")
    effect_value += (effect_value * caster_player.get_outgoing_damage(effect_school) * 0.01)
  #  print(f"a1: {effect_value}")

    # gets caster's aura
    if Aura in caster_player.get_effects():
        print("inside")
        # do stuff

    # gets any blades/weaknesses caster may have
    if Charm in caster_player.get_effects():
        print("blade")
        # do stuff

    # gets the global
    b = match_obj.getBubble()

    if b.school == effect_school:
      #  print(f"Found bubble with value {b.value}")
        effect_value += effect_value * b.value * 0.01
    
  #  print(f"post-bubble effect_value: {effect_value}")

    # gets any auras the enemy may have
    enemy_aura = next( (effect for effect in enemy_player.effects if isinstance(effect, Aura)), None )
    if enemy_aura is not None:
        adj = enemy_aura.adj

        print(json.dumps(adj, indent=4))

        # ignore if not correct school
        if adj["SCHOOL"] in (effect_school, "UNIVERSAL"):
            # ignore if not shield/trap type aura
            if adj["TYPE"] == "SHIELD":
                effect_value -= effect_value * adj["VALUE"] * 0.01
            elif adj["TYPE"] == "TRAP":
                effect_value += effect_value * adj["VALUE"] * 0.01

  #  print(f"post-aura effect_value: {effect_value}")


    # gets enemy shields/traps
    enemy_wards = [ effect for effect in enemy_player.effects if isinstance(effect, Ward) ]

    used_families = set()

    for ward in enemy_wards:
        if ward.school in (effect_school, "UNIVERSAL"):
            if ward.family in used_families:
                continue
            used_families.add(ward.family)
            print(f"Ward used: {ward.school} of val {ward.value}")
            effect_value = ward.mod_damage(effect_value)
            enemy_player.del_effect(ward)
    
  #  print(f"Post-ward effect_value: {effect_value}")

    # gets enemy resist
    enemy_res = enemy_player.get_incoming_resist(effect_school)
  #  print(f"enemy res: {enemy_res}")
    effect_value -= effect_value * enemy_res * 0.01
  #  print(f"Post-resist effect_value: {effect_value}")

    abs_target.dec_health(effect_value)
    print(f"Does {effect_value} damage!")
    print(f"{abs_target.name} HEALTH: {abs_target.curr_health}")

    # a3 = a2 * enemy_player.get_charms
    # a4 = a3 * get_global
    # a5 = a4 * caster_player.get_aura
    # a6 = a5 * caster_player.get_wards
    # a7 = a6 * enemy_player.get_incoming_res
    # abs_target.dec_health(effect_value)

 #   print(f"{abs_target.name} HEALTH: {abs_target.get_health()}")

def play_gambit(caster_player, enemy_player, effect):
    gambit_cause = effect.get("CAUSE")
    gambit_effect = effect.get("PER_EFFECT")

  #  print(json.dumps(gambit_cause, indent=4))
  #  print(json.dumps(gambit_effect, indent=4))

    abs_target = get_target(caster_player, enemy_player, gambit_cause)

    match gambit_cause.get("ACTION"):
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
                    abs_target = get_target(caster_player, enemy_player, gambit_effect)

                    per_effect_school = gambit_effect.get("SCHOOL")
                    per_effect_value = gambit_effect.get("VALUE")
                    per_effect_family = gambit_effect.get("FAMILY")

                    if per_effect_school == "TARGET_SCHOOL":
                        per_effect_school = abs_target.school

                    jel = Trap(per_effect_school, per_effect_value, per_effect_family)

                    match_obj.add_effect(abs_target, jel)


def cast_spell(match_obj, caster_player, enemy_player, spell_data):
    # if a player passes that turn, skip
    if spell_data in (None, "NONE"):
        return

    spell_effects = spell_data.get("EFFECTS")

    # loop through the effects of the spell
    # then apply them to the right player in match_obj
    for effect in spell_effects:
        effect_type = effect.get("TYPE")

        print(f"Adding effect: {effect_type}")


        match effect_type:
            case "SINGLE_DAMAGE":
                do_damage(match_obj, caster_player, enemy_player, effect)

            case "TRAP":
                abs_target = get_target(caster_player, enemy_player, effect)

                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                effect_family = effect.get("FAMILY")

                # abs_target = match_obj.getTTarget(caster, effect_target)

                jel = Trap(effect_school, effect_value, effect_family)

                match_obj.add_effect(abs_target, jel)
            case "AURA":
                abs_target = get_target(caster_player, enemy_player, effect)

                bor = Aura(
                    effect.get("DURATION"),
                    effect.get("ADJ")
                )

                # checks if target already has an aura effect
                has_aura = next( (effect for effect in abs_target.effects if isinstance(effect, Aura)), None )

                # if aura, delete
                if has_aura:
                    abs_target.del_effect(has_aura)

                match_obj.add_effect(abs_target, bor)

            case "BACKLASH":
                ba = Backlash(
                    effect.get("DURATION"),
                    effect.get("VALUE_PER_TURN"),
                    effect.get("CONDITION")
                )

                match_obj.add_effect(caster_player, ba)

            case "GAMBIT":
                play_gambit(caster_player, enemy_player, effect)

            case "SHIELD":
                abs_target = get_target(caster_player, enemy_player, effect)

                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                effect_family = effect.get("FAMILY")

                if effect_school == "TARGET_SCHOOL":
                        effect_school = enemy_player.school

                amount = effect.get("AMOUNT", 1)
                
                for _ in range(amount):
                    hehe = Shield(effect_school, effect_value, effect_family)
                    match_obj.add_effect(abs_target, hehe)

            case "BUBBLE":
                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")
                kori = Bubble(effect_school, effect_value)
                match_obj.change_bubble(kori)


# match_obj is what is changing over time --
# "match" var just refers to the raw match json code

# this function starts the match by reading from the match file
# it uses match_obj to determine the parameters of the match
# (player info)
def start_match(match_obj):
    try:
        with open("w101_ezra_jason.json", "r") as f:
            match = json.load(f)
    except json.JSONDecodeError:
        print("ERROR! FAILED TO DECODE JSON!")

    try:
        with open("w101_spells.json") as f:
            spells = json.load(f)
    except json.JSONDecodeError:
        print("ERROR! FAILED TO DECODE JSON!")

    insert_starting_conditions(match_obj)

    # puts every entry read from w101_spells.json into a dict
    spell_lookup = { spell["SPELL"]: spell for spell in spells }

    #df = pd.DataFrame(match)

    print(f"P1 HEALTH: {match_obj.getPlayer1().get_health()}")
    print(f"P2 HEALTH: {match_obj.getPlayer2().get_health()}")

    for turn in match:
        round = turn.get("ROUND")
        caster = turn.get("CASTER")

        # caster stored in the match obj has definite names for players
        # these directly map on to the actual player names via matchups.json
        if caster == "PLAYER1":
            caster_player = match_obj.getPlayer1()
            enemy_player = match_obj.getPlayer2()
        elif caster == "PLAYER2":
            caster_player = match_obj.getPlayer2()
            enemy_player = match_obj.getPlayer1()

      #  p1e1 = turn.get("PLAYER1_EFFECTS1", [])
        p1e1 = match_obj.getPlayer1().get_effects()
        p2e1 = match_obj.getPlayer2().get_effects()

        print("----")

        # only activate effect of the player who is casting
        # this is where backlash is taken and where backlash eats
        if caster == "PLAYER1":
            for effect in p1e1:
                effect.begin_round()
                if effect.expired():
                    if effect.type == "BACKLASH":
                        perc_dmg = effect.accumulated
                        dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
                        print(f"{caster_player.name} takes {dmg_taken} damage!")
                        caster_player.dec_health(dmg_taken)
                        print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
                    caster_player.del_effect(effect)
        else:
            for effect in p2e1:
                effect.begin_round()
                if effect.expired():
                    if effect.type == "BACKLASH":
                        perc_dmg = effect.accumulated
                        dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
                        print(f"{caster_player.name} takes {dmg_taken} damage!")
                        caster_player.dec_health(dmg_taken)
                        print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
                    caster_player.del_effect(effect)

        caster_backlash = next( (effect for effect in caster_player.effects if isinstance(effect, Backlash)), None )
        print(f"caster_backlash: {caster_backlash}")
        if caster_backlash:
            eat_effect = caster_backlash.condition["EFFECT"]
        #  eat_target = caster_backlash.condition["TARGET"]
            eat_target = get_target(caster_player, enemy_player, caster_backlash.condition)
            
            ate = False
          #  print(eat_target.name)
            print(f"eat_effect: {eat_effect}")
            for effect in reversed(eat_target.effects):
                if effect.type == eat_effect:
                    eat_target.del_effect(effect)
                    print(f"eating effect: {effect} from {eat_target.name}")
                    ate = True
                    break

            if not ate:
                caster_backlash.inc_backlash()
                print("Did not eat an effect")

        print_effects(match_obj.getPlayer1())
        print_effects(match_obj.getPlayer2())
        # gets the spell name cast on that turn from w101_ezra_jason.json
        spell_name = turn.get("SPELL")

        # if a player passes that turn, skip
        if spell_name in (None, "NONE"):
            print(f"**PASS")
            print(f"Round {round}: {caster_player.name} PASSES")

        if spell_name not in (None, "NONE"):
            print(f"**SPELL: {spell_name}")
            # get data from that spell to add to match
            spell_data = spell_lookup.get(spell_name)

            print_turn_info(round, caster_player, spell_name)

            cast_spell(match_obj, caster_player, enemy_player, spell_data)

        p1e2 = match_obj.getPlayer1().get_effects()
        p2e2 = match_obj.getPlayer2().get_effects()

        if caster == "PLAYER1":
            for effect in p1e2:
                effect.end_round()
        else:
            for effect in p2e2:
                effect.end_round()

        print_effects(match_obj.getPlayer1())
        print_effects(match_obj.getPlayer2())

            # if hasattr(effect, "duration"):
            #     print(f"Duration: {effect.duration}")
     


    # ward value not specified in cases:
    # gambit spells (check if exclusive case or not)
    # backlash conditions

    # gambit spells are structured
    # type: gambit
    # cause         effect      else
    # cause: what effects to eat
    # effect: what happens if cause is fulfilled
    # else: what happens if cause is not fulfilled

    # backlash spells
    # backlash spells always eats up an effect of any school and any value

try:
    with open("w101_players.json", "r") as f:
        players = json.load(f)
except json.JSONDecodeError:
    print("ERROR! FAILED TO DECODE JSON!")

try:
    with open("w101_matchups.json", "r") as f:
        matchups = json.load(f)
except json.JSONDecodeError:
    print("ERROR! FAILED TO DECODE JSON!")

player_lookup = { player["NAME"]: player for player in players }

match_dat = []

for match in matchups:
    p1_name = match.get("PLAYER1")
    p2_name = match.get("PLAYER2")

    p1_dat = player_lookup.get(p1_name)
    p2_dat = player_lookup.get(p2_name)

    # name
    # lvl
    # school
    # 2 school
    # health
    # outoging dmg
    # inc resist
    # acc
    # crit
    # block
    # pierce
    # pip conv
    # shad

    p1_obj = Player(
        p1_dat.get("NAME"),
        p1_dat.get("SCHOOL"),
        p1_dat.get("SECONDARY_SCHOOL"),
        p1_dat.get("LEVEL"),
        p1_dat.get("MAX_HEALTH"),
        p1_dat.get("OUTGOING_DAMAGE"),
        p1_dat.get("INCOMING_RESIST"),
        p1_dat.get("PIERCE")
    )

    p2_obj = Player(
        p2_dat.get("NAME"),
        p2_dat.get("SCHOOL"),
        p2_dat.get("SECONDARY_SCHOOL"),
        p2_dat.get("LEVEL"),
        p2_dat.get("MAX_HEALTH"),
        p2_dat.get("OUTGOING_DAMAGE"),
        p2_dat.get("INCOMING_RESIST"),
        p2_dat.get("PIERCE")
    )

    match_obj = Match(p1_obj, p2_obj, 0)
    match_dat.append(match_obj)

#print(match_dat[0].p1.name)
start_match(match_dat[0])
#start_match(match_obj)
# for match in match_dat:
#     print(match.p1.name)

# SLOAN
# ARLEN FURY
# OMARI SHADOW
# CALAMITY CURSE
# ALEX PYRE
# MARIA SUN
# ISAIAH EMERALD
# JASON NIGHT
# EZRA POLARKNIGHT
# JOHN WEAVE
# DUNCAN
# BLAZE MOON
# AEDAN LEGEND
# PAUL TIME
# ALEX PYRE
# SUMI

# # CLEAR GAMBIT CONVERT EXTEND PUSH CONFUSE SWAP STEAL
# # NEG CHARMS, NEG WARD GO ON ENEMY
# # POS CHARMS, POS WARD GO ON SELF