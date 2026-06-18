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

def cast_spell(caster_player, enemy_player, spell_data):
    # if a player passes that turn, skip
    if spell_data in (None, "NONE"):
        return

    spell_effects = spell_data.get("EFFECTS")

    # loop through the effects of the spell
    # then apply them to the right player in match_obj
    for effect in spell_effects:
        effect_type = effect.get("TYPE")

        if effect_type == "GAMBIT":
            print("gambit!")
            gambit_cause = effect.get("CAUSE")
            print(effect.get("CAUSE"))
            gambit_effect = effect.get("PER_EFFECT")
            print(effect.get("PER_EFFECT"))

            match gambit_cause.get("ACTION"):
                case "CLEAR":
                    pass

        if effect_type == "SINGLE_DAMAGE":
            effect_target = effect.get("TARGET")

            if effect_target == "SELF":
                abs_target = caster_player
            elif effect_target == "ENEMY":
                abs_target = enemy_player

            effect_school = effect.get("SCHOOL")
            effect_value = effect.get("VALUE")

            abs_target.dec_health(effect_value)

            print(f"{effect_target} HEALTH: {abs_target.get_health()}")

            # lavendar = Damage(abs_target, effect_school, effect_value)
            # lorri = Effect(effect_type, lavendar)

            # match_obj.add_effect(abs_target, lorri)

        if effect_type == "WARD":
            effect_target = effect.get("TARGET")

            if effect_target == "SELF":
                abs_target = caster_player
            elif effect_target == "ENEMY":
                abs_target = enemy_player

            # if caster == "PLAYER1":
            #     if effect_target == "SELF":
            #         abs_target = match_obj.getPlayer1()
            #     elif effect_target == "ENEMY":
            #         abs_target = match_obj.getPlayer2()
            # elif caster == "PLAYER2":
            #     if effect_target == "SELF":
            #         abs_target = match_obj.getPlayer2()
            #     elif effect_target == "ENEMY":
            #         abs_target = match_obj.getPlayer1()

            effect_polarity = effect.get("POLARITY")
            effect_school = effect.get("SCHOOL")
            effect_value = effect.get("VALUE")

            # abs_target = match_obj.getTTarget(caster, effect_target)

            jel = Ward(effect_polarity, effect_school, effect_value)

            match_obj.add_effect(abs_target, jel)
        
        if effect_type == "AURA":
            effect_target = effect.get("TARGET")

            if effect_target == "SELF":
                abs_target = caster_player
            elif effect_target == "ENEMY":
                abs_target = enemy_player
            # if caster == "PLAYER1":
            #     if effect_target == "SELF":
            #         abs_target = match_obj.getPlayer1()
            #     elif effect_target == "ENEMY":
            #         abs_target = match_obj.getPlayer2()
            # elif caster == "PLAYER2":
            #     if effect_target == "SELF":
            #         abs_target = match_obj.getPlayer2()
            #     elif effect_target == "ENEMY":
            #         abs_target = match_obj.getPlayer1()

            bor = Aura(
                effect.get("DURATION"),
                effect.get("ADJ")
            )

            match_obj.add_effect(abs_target, bor)

        if effect_type == "BACKLASH":
            # if effect_target == "SELF":
            #     abs_target = caster_player
            # elif effect_target == "ENEMY":
            #     abs_target = enemy_player
            # if caster == "PLAYER1":
            #     abs_target = match_obj.getPlayer1()
            # else:
            #     abs_target = match_obj.getPlayer2()

            ba = Backlash(
                effect.get("DURATION"),
                effect.get("VALUE_PER_TURN"),
                effect.get("CONDITION")
            )

            match_obj.add_effect(caster_player, ba)

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

        cast_spell(caster_player, enemy_player, spell_data)

        p1e2 = match_obj.getPlayer1().get_effects()

        for effect in p1e2:
        #    print(effect)
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