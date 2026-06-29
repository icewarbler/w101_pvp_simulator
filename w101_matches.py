import json
import pandas as pd
import math
from w101_effects import Effect
from w101_effects import Single_Damage
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

def insert_starting_conditions(match_obj):
    p1 = match_obj.getPlayer1() # ezra
    p2 = match_obj.getPlayer2() # jason

    match_obj.change_bubble(Bubble("FIRE", 25))

  #  print(f"{match_obj.global_effect}")

    p1.add_effect(Trap("FIRE", 65, None))
    adj = [{
        "TYPE": "SHIELD",
        "SUBTYPE": "DAMAGE",
        "SCHOOL": "UNIVERSAL",
        "VALUE": 20
    }]
    p1.aura = Aura(2, adj)

    p2.add_effect(Trap("FIRE", 30, None))
    p2.add_effect(Trap("ICE", 30, None))
    p2.add_effect(Trap("STORM", 30, None))

# fire ice storm (traps/shields) -> put on order
# ice storm fire (blades) -> put on order
# cleanse charm removes fire weakness - ice/storm left
# pierce removes storm shield - fire/ice left

def cast_spell(match_obj, caster_player, enemy_player, spell_data):
    # if a player passes that turn, skip
    if spell_data in (None, "NONE"):
        return

    spell_effects = spell_data.get("EFFECTS")


    # loop through the effects of the spell
    # then apply them to the right player in match_obj
    for effect in spell_effects:
        effect_type = effect["TYPE"]

        print(f"Adding effect: {effect_type}")

        effect_class = Effect.registry[effect["TYPE"]]
        effect_obj = effect_class.from_json(effect)

      #  print(effect_obj)

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

                amount = effect.get("AMOUNT", 1)

                print(effect_obj)

                if effect_obj.type == "AURA":
                    abs_target.aura = effect_obj
                    continue
                
                for _ in range(amount):
                    abs_target.add_effect(effect_obj)

            
            case "MATCH":
                match_obj.global_effect = effect_obj

            case None:
                effect_obj.apply(match_obj, caster_player, enemy_player, effect)

      #  print(f"{effect_obj} has persistance: {effect_obj.is_persistant()}")
        # if effect_obj.is_persistant():
        #     abs_target = get_target(caster_player, enemy_player, effect)
        #     abs_target.add_effect(effect_obj)
        # else:
        #     effect_obj.apply(match_obj, caster_player, enemy_player)

        continue


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
    spell_lookup = { spell["ID"]: spell for spell in spells }

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
        # this is where backlash is taken
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

        # this is where backlash eats
        caster_backlash = next( (effect for effect in caster_player.effects if isinstance(effect, Backlash)), None )
        print(f"caster_backlash: {caster_backlash}")
        if caster_backlash:
            eat_effect = caster_backlash.condition["EFFECT"]
            effect_target = caster_backlash.condition["TARGET"]

            if effect_target == "SELF":
                eat_target = caster_player
            elif effect_target == "ENEMY":
                eat_target = enemy_player
            
            ate = False

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
        
        if caster_player.aura is not None:
            print("Caster aura:")
            caster_player.aura.end_round()
            print(caster_player.aura)
        
        if enemy_player.aura is not None:
            print("Enemy aura:")
            print(enemy_player.aura)

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

#test_run(match_dat[0])
start_match(match_dat[0])

#print(match_dat[0].p1.name)
# start_match(match_dat[0])
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