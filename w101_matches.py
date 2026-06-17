import json
import pandas as pd
from w101_effects import Effect
from w101_effects import Damage
from w101_effects import Ward
from w101_effects import Charm
from w101_effects import Backlash
from w101_effects import Aura
from w101_player import Player
from w101_match_setup import Match

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

    rows = []

    for turn in match:
        round = turn.get("ROUND")
        caster = turn.get("CASTER")

        p1e1 = turn.get("PLAYER1_EFFECTS1", [])
        p2e1 = turn.get("PLAYER2_EFFECTS1", [])

        for effects in p1e1:
         #   print(effects)
            effects.get("TURNS_LEFT")
            print(effects.get("TURNS_LEFT"))


        # gets the spell name cast on that turn from w101_ezra_jason.json
        spell_name = turn.get("SPELL")

        # if a player passes that turn, skip
        if spell_name in (None, "NONE"):
            continue

        # get data from that spell to add to match
        spell_data = spell_lookup.get(spell_name)

        spell_effects = spell_data.get("EFFECTS")

        # loop through the effects of the spell
        # then apply them to the right player in match_obj
        for effect in spell_effects:
            effect_type = effect.get("TYPE")

            if effect_type == "SINGLE_DAMAGE":
                effect_target = effect.get("TARGET")

                if caster == "PLAYER1":
                    abs_target = match_obj.getPlayer2()
                else:
                    abs_target = match_obj.getPlayer1()

                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                lavendar = Damage(abs_target, effect_school, effect_value)
                lorri = Effect(effect_type, lavendar)

            match_obj.add_effect(abs_target, lorri)
            
            rows.append({
                    **{f"EFFECT_{k}": v for k, v in effect.items()}
            })

            if effect_type == "WARD":
                effect_target = effect.get("TARGET")

                if caster == "PLAYER1":
                    if effect_target == "SELF":
                        abs_target = match_obj.getPlayer1()
                    elif effect_target == "ENEMY":
                        abs_target = match_obj.getPlayer2()
                elif caster == "PLAYER2":
                    if effect_target == "SELF":
                        abs_target = match_obj.getPlayer2()
                    elif effect_target == "ENEMY":
                        abs_target = match_obj.getPlayer1()

                effect_polarity = effect.get("POLARITY")
                effect_school = effect.get("SCHOOL")
                effect_value = effect.get("VALUE")

                # abs_target = match_obj.getTTarget(caster, effect_target)

                jel = Ward(effect_polarity, effect_school, abs_target, effect_value)
                lauren = Effect(effect_type, jel)

                match_obj.add_effect(abs_target, lauren)
            
            if effect_type == "AURA":
                effect_target = effect.get("TARGET")

                if caster == "PLAYER1":
                    if effect_target == "SELF":
                        abs_target = match_obj.getPlayer1()
                    elif effect_target == "ENEMY":
                        abs_target = match_obj.getPlayer2()
                elif caster == "PLAYER2":
                    if effect_target == "SELF":
                        abs_target = match_obj.getPlayer2()
                    elif effect_target == "ENEMY":
                        abs_target = match_obj.getPlayer1()

                bor = Aura(
                    effect.get("DURATION"),
                    effect.get("VALUE_PER_TURN"),
                    effect.get("ADJ")
                )
                jerry = Effect(effect_type, bor)

                match_obj.add_effect(abs_target, jerry)

            if effect_type == "BACKLASH":
                if caster == "PLAYER1":
                    abs_target = match_obj.getPlayer1()
                else:
                    abs_target = match_obj.getPlayer2()

                ba = Backlash(
                    effect.get("DURATION"),
                    effect.get("VALUE_PER_TURN"),
                    effect.get("CONDITION")
                )
                ralp = Effect(effect_type, ba)

                match_obj.add_effect(abs_target, ralp)

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