import json
import pandas as pd
from w101_effects import Effect
from w101_effects import Damage
from w101_effects import Charm
from w101_effects import Trap
from w101_effects import Backlash
from w101_effects import Aura
from w101_player import Player
from w101_match_setup import Match


def print_turn_info(round, caster_player, spell_name):
    print(f"Round {round}: {caster_player.name} casts {spell_name}")

def get_target(caster_player, enemy_player, effect):
    effect_target = effect.get("TARGET")

    if effect_target == "SELF":
        target = caster_player
    elif effect_target == "ENEMY":
        target = enemy_player
    return target

def play_gambit(caster_player, enemy_player, effect):
    print("gambit!")
    gambit_cause = effect.get("CAUSE")
    print(effect.get("CAUSE"))
    gambit_effect = effect.get("PER_EFFECT")
    print(effect.get("PER_EFFECT"))

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
        #  print(to_remove)

        #   print(abs_target.get_effects())

            amount = len(to_remove)

            print(f"amount: {amount}")


            for effect in to_remove:
                abs_target.del_effect(effect)
            #    print(abs_target.get_effects())

            per_effect_type = gambit_effect.get("TYPE")
            
            for _ in range(amount):
                if per_effect_type == "TRAP":
                    abs_target = get_target(caster_player, enemy_player, gambit_effect)

                    per_effect_school = gambit_effect.get("SCHOOL")
                    per_effect_value = gambit_effect.get("VALUE")


                    jel = Trap(per_effect_school, per_effect_value)

                    match_obj.add_effect(abs_target, jel)


def cast_spell(caster_player, enemy_player, spell_data):
    # if a player passes that turn, skip
    if spell_data in (None, "NONE"):
        return

    spell_effects = spell_data.get("EFFECTS")

    # loop through the effects of the spell
    # then apply them to the right player in match_obj
    for effect in spell_effects:
        effect_type = effect.get("TYPE")


        match effect_type:
            case "SINGLE_DAMAGE":
                abs_target = get_target(caster_player, enemy_player, effect)

                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                abs_target.dec_health(effect_value)

                print(f"{abs_target.name} HEALTH: {abs_target.get_health()}")
            case "TRAP":
                abs_target = get_target(caster_player, enemy_player, effect)

                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                # abs_target = match_obj.getTTarget(caster, effect_target)

                jel = Trap(effect_school, effect_value)

                match_obj.add_effect(abs_target, jel)
            case "AURA":
                abs_target = get_target(caster_player, enemy_player, effect)

                bor = Aura(
                    effect.get("DURATION"),
                    effect.get("ADJ")
                )

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

        # for effect in p1e1:
        #     print(effect)
         #   effect.end_round()
            # effect_obj = effect.get_effect_obj()
            # print(effect_obj)
            # if not effect_obj.duration:
            #     print("none")

        p2e1 = turn.get("PLAYER2_EFFECTS1", [])

        # gets the spell name cast on that turn from w101_ezra_jason.json
        spell_name = turn.get("SPELL")

        # if a player passes that turn, skip
        if spell_name in (None, "NONE"):
            continue

        # get data from that spell to add to match
        spell_data = spell_lookup.get(spell_name)

        print_turn_info(round, caster_player, spell_name)

        cast_spell(caster_player, enemy_player, spell_data)

        p1e2 = match_obj.getPlayer1().get_effects()

        for effect in p1e2:
            print(effect)
            effect.end_round()

            if hasattr(effect, "duration"):
                print(f"Duration: {effect.duration}")
     


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
    )

    p2_obj = Player(
        p2_dat.get("NAME"),
        p2_dat.get("SCHOOL"),
        p2_dat.get("SECONDARY_SCHOOL"),
        p2_dat.get("LEVEL"),
        p2_dat.get("MAX_HEALTH"),
    )

    match_obj = Match(p1_obj, p2_obj, 0)

start_match(match_obj)


# DOOMED MONSTER HIDE CROWN
# FITZHUMES ROVER GEAR
# DOOMED ABOMINATION STALERS

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

# # CLEAR GAMBIT CONVERT EXTEND PUSH CONFUSE SWAP STEAL
# # NEG CHARMS, NEG WARD GO ON ENEMY
# # POS CHARMS, POS WARD GO ON SELF