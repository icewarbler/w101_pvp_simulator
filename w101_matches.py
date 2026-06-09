import json
import pandas as pd
from w101_effects import Effect
from w101_player import Player

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
    p1_e1 = turn.get("PLAYER1_EFFECTS1", [])

    spell_name = turn.get("SPELL")

    spell_data = spell_lookup.get(spell_name)

    if spell_data:
        spell_type = spell_data.get("TYPE")
        print(spell_type)

        spell_effects = spell_data.get("EFFECTS")
        print(spell_effects)

        for effect in spell_effects:
            print(effect.get("TYPE"))
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