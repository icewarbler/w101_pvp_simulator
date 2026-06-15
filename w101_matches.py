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

# "PLAYER1_EFFECTS1": [
#             {
#                 "TYPE": "AURA",
#                 "ROUNDS_LEFT": 1,
#                 "ADJ": [
#                     {
#                        "TYPE": "WARD",
#                         "POLARITY": "POS",
#                         "SUBTYPE": "DAMAGE",
#                         "SCHOOL": "GLOBAL",
#                         "VALUE": 25 
#                     }
#                 ]
#             },
#             {
#                 "TYPE": "WARD",
#                 "SUBTYPE": "DAMAGE",
#                 "POLARITY": "NEG",
#                 "SCHOOL": "FIRE",
#                 "VALUE": 65
#             },
#             {
#                 "TYPE": "WARD",
#                 "SUBTYPE": "DAMAGE",
#                 "POLARITY": "POS",
#                 "SCHOOL": "FIRE",
#                 "QUANTITY": 3,
#                 "VALUE": 80
#             },
#             {
#                 "TYPE": "BACKLASH",
#                 "DURATION": 3,
#                 "VALUE_PER_TURN": 5,
#                 "TURNS_LEFT": 3,
#                 "ACCUMULATED": 5,
#                 "VALUE_TYPE": "PERCENT_MAX_HEALTH",
#                 "CONDITION": {
#                     "TYPE": "WARD",
#                     "POLARITY": "NEG",
#                     "TARGET": "PLAYER2"
#                 }
#             }
#         ],

# APPLIES 3 80% SHIELDS OF TARGETS SCHOOL TO SELF - dark weaver

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

    spell_lookup = { spell["SPELL"]: spell for spell in spells }

    #df = pd.DataFrame(match)

    rows = []
    #effect_fields = ["TYPE", "VALUE", "TARGET"]

    for turn in match:
        caster = turn.get("CASTER")

        target = turn.get("TARGET")

        # abs_target = ""

        # if caster == "PLAYER1":
        #     if target == "SELF":
        #         abs_target = match_obj.getPlayer1()
        #     elif target == "ENEMY":
        #         abs_target = match_obj.getPlayer2()
        # elif caster == "PLAYER2":
        #     if target == "SELF":
        #         abs_target = match_obj.getPlayer2()
        #     elif target == "ENEMY":
        #         abs_target = match_obj.getPlayer1()

        p1_e1 = turn.get("PLAYER1_EFFECTS1", [])

        spell_name = turn.get("SPELL")

        spell_data = spell_lookup.get(spell_name)

        if spell_data:
            spell_type = spell_data.get("TYPE")
        #  print(spell_type)

            spell_effects = spell_data.get("EFFECTS")
        #  print(spell_effects)

            for effect in spell_effects:
                effect_type = effect.get("TYPE")

                if effect_type == "SINGLE_DAMAGE":
                    effect_target = effect.get("TARGET")

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

                    if caster == "PLAYER1":
                        abs_target = match_obj.getPlayer2()
                    else:
                        abs_target = match_obj.getPlayer1()
                    
                    # abs_target = match_obj.getTTarget(caster, effect_target)

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

# self.duration = duration
#         self.value_per_turn = value_per_turn
#         self.condition = condition

#         self.curr_turn = 0
#         self.accumulated = value_per_turn
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



        #         class Ward:
        # def __init__(
        #         self,
        #         polarity,
        #         school,
        #         target,
        #         value
        # ):
        #     self.polarity = polarity
        #     self.school = school
        #     self.target = target
        #     self.value = value

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
    # self.duration = duration
    #         self.value_per_turn = value_per_turn
    #         self.condition = condition

    #         self.curr_turn = 0
    #         self.accumulated = value_per_turn

    # "TYPE": "BACKLASH",
    #                 "DURATION": 3,
    #                 "VALUE_PER_TURN": 5,
    #                 "CONDITION": {
    #                     "EFFECT": "NEG_WARD",
    #                     "TARGET": "ENEMY"
    #                 }
    # backlash spells always eats up an effect of any school and any value


                # if effect_type == "WARD":
                #     effect_polarity = effect.get("POLARITY")
                #     effect_school = effect.get("SCHOOL")
                #     effect_target = effect.get("TARGET")
                #     effect_value = effect.get("VALUE")

                #     jel = Ward(effect_polarity, effect_school, effect_target, effect_value)
                #     lauren = Effect(effect_type, jel)

                #     abs_target.add_effect()

                    # match_obj.add_effect(effect_target, lauren)
                    
    for row in rows: print(row)

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


# class Player:
#     def __init__(
#             self, 
#             name, 
#             school,
#             secondary_school, 
#             max_health, 
#             curr_health, 
#             pips
#         ):
#         self.name = name
#         self.school = school
#         self.secondary_school = secondary_school

#         self.max_health = max_health
#         self.curr_health = curr_health

#         self.pips = pips

#         self.effects = []

        # if any(x in ["WARD", "MANIPULATION", "AURA"] for x in spell_type):
        #     spell_effects = spell_data.get("EFFECTS")
        #     print(spell_effects)
        #     tommy = Effect(spell_type, spell_data)
        #    # print(tommy)
        #     effect_obj = tommy.get_effect_obj()
        #     print(tommy.get_effect_obj())

            #     blade = Effect(
    #         effect_type = "CHARM",
    #         value = getCurrentSpell().effects.charm.value

    #     )

 
    # spelle = spell_lookup.get(spell_name)
    # school = spelle.get("SCHOOL") if spelle else None

    # for effect in p1_e1:
    #     rows.append({
    #         "SPELL": turn["SPELL"],
    #         "SCHOOL": school,
    #         **{"EFFECT_TYPE": effect.get("TYPE")}
    #     })

# effects_df = pd.DataFrame(rows)
# print(effects_df)
# gets from column inside a column. value=None if not defined in json
#df["MODIFIER_TYPE"] = df["MODIFIERS"].apply(lambda x: x[0]["TYPE"] if isinstance(x, list) and len(x) > 0 else None)

#df["AURA_ADJ"] = df["PLAYER1_EFFECTS1"].apply(lambda x: x[0]["ADJ"]["TYPE"] if isinstance(x, list) and len(x) > 0 else None)

#print(df.iloc[0]["PLAYER1_EFFECTS1"])

#print(df[["SPELL", "CASTER", "TARGET", "PLAYER1_PIPS"]])
#print(df[0]["PLAYER1_EFFECT1"]["TYPE"]["ADJ"])

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

# find the average damage per pip by school
# print(df.groupby("SCHOOL")["PIPCOST"].mean())

# cast steal pip




# ROUNDS = []
# COUNT = 0
# START = False

# # CLEAR GAMBIT CONVERT EXTEND PUSH CONFUSE SWAP STEAL
# # NEG CHARMS, NEG WARD GO ON ENEMY
# # POS CHARMS, POS WARD GO ON SELF


# while True:
#     # { 
#     # "RND": ["START", "END"], 
#     # "PLAYER": ["ALEX", "MARIA"], 
#     # "SPELL": [""], 
#     # "HEALTH": "", 
#     # "PIPS": "", 
#     # "DEBUF": "", 
#     # "BUFF": ""
#     # }   
#     SPELL = input("SPELL: ")
#     HEALTH = input("HEALTH: ")
#     PIPS = input("PIPS: ")
#     DEBUF = input("DEBUF")
#     BUFF = input("BUFF")
#     if COUNT % 3 == 0:
#         START = not START

#     if START:
#         RND = "START"
#     else:
#         RND = "END"

#     if COUNT % 4 in (0, 3):
#         PLAYER = "ALEX"
#     else:
#         PLAYER = "MARIA"

#     COUNT += 1

#     ROUNDS.append({
#         "RND": [RND],
#         "PLAYER": ["ALEX", "MARIA"],
#     })
#     # 1 2 3 7 8 9- start; 4 5 6 10 11 12- end
#     # 0 1 2 6 7 8 - START; 3 4 5 9 10 11 - END

#     # ALEX: 0 2 5 7 8 10 13 15
#     # MARIA: 1 3 4 6 9 11 12 14

#     # ALEX: 0 3 4 7 8 11 12 15
#     # MARIA: 1 2 5 6 9 10 13 14