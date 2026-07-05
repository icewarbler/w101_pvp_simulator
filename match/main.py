import json
import pandas as pd
import math
from effects import Effect
from effects import Single_Damage
from effects import Charm
from effects import Ward
from effects import Trap
from effects import Shield
from effects import Backlash
from effects import Aura
from effects import Bubble
from effects import DOT
from effects import Bomb_DOT
from player import Player
from match import Match
from spell_instance import SpellInstance
from pip import Pip

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

    # p1.pips.update({
    #     "DEATH": 1,
    #     "LIFE": 3
    # })

    p1.pips.append(Pip("DEATH"))
    p1.pips.append(Pip("LIFE"))
    p1.pips.append(Pip("LIFE"))
    p1.pips.append(Pip("LIFE"))

    p1.shadpips = 1
    p2.shadpips = 2

    # p2.pips.update({
    #     "REG": 2,
    #     "FIRE": 1,
    #     "MYTH": 1,
    #     "STORM": 1
    # })

    p2.pips.append(Pip("REG"))
    p2.pips.append(Pip("REG"))
    p2.pips.append(Pip("FIRE"))
    p2.pips.append(Pip("MYTH"))
    p2.pips.append(Pip("STORM"))

def handle_pips(caster_player, context):
  #  before_casting = {school: caster_player.pips[school] for school in caster_player.pips}
    print(f"{caster_player.name} has {[pip for pip in caster_player.pips]} pips and {caster_player.shadpips} shad pips before casting")

    priority_school = context.spell.get("SCHOOL")
    caster_school = caster_player.school
    print(f"spell school: {priority_school}; caster school: {caster_school}")
    if caster_school == priority_school:
        use_power = True
    else:
        use_power = False

    # eats from school pips first
    for school, cost in context.schoolpips.items():
        print(f"Found a school pip: {school}")
        to_rem = next((pip for pip in caster_player.pips if pip.school == school), None)
        if to_rem is None:
            raise AssertionError("Impossible to cast spell without required school pip(s)!")
        caster_player.remove_pip(to_rem)

    while context.pips > 0:
        odd = True if context.pips % 2 == 1 else False

        # even number of pips means no reg pips consumed
        if not odd:
            school_pip = next((pip for pip in caster_player.pips if pip.school == priority_school), None)
            if school_pip is not None:
            #    print(f"Removing even pip: {not_reg_pip}")
                print(f"Removing school pip: {school_pip}")
                caster_player.remove_pip(school_pip)
            else:
                if use_power:
                    not_reg_pip = next((pip for pip in caster_player.pips if pip.school != "REG"), None)
                    if not_reg_pip is not None:
                        print(f"removing not-reg pip: {not_reg_pip}")
                        caster_player.remove_pip(not_reg_pip)
                        context.pips -= 2
                        continue
                    # if not_reg_pip is None:
                    #     reg_pips = [pip for pip in caster_player.pips if pip.school == "REG"]
                
                    #     # if there are no non-regular pips, it is assumed that there are enough regular pips (2)
                    #     # uses 2 regular pips
                    #     for i, pip in enumerate(reg_pips):
                    #         if i >= 2:
                    #             break 
                    #         caster_player.remove_pip(pip)
                    # else:
                    #     caster_player.remove_pip(not_reg_pip)

                # there must be reg pips or else the spell should not cast
                reg_pips = [pip for pip in caster_player.pips if pip.school == "REG"]

                for i, pip in enumerate(reg_pips):
                    if i >= 2:
                        break 
                    print(f"removing reg pip: {pip}")
                    caster_player.remove_pip(pip)

            context.pips -= 2

            #    print(f"no regular pips!")
            #     reg_pips = [pip for pip in caster_player.pips if pip.school == "REG"]
                
            #     # if there are no non-regular pips, it is assumed that there are enough regular pips (2)
            #     # uses 2 regular pips
            #     for i, pip in enumerate(reg_pips):
            #         if i >= 2:
            #             break 
            #         caster_player.remove_pip(pip)
            # context.pips -= 2
                
        # odd number means try to consume one reg pip
        # if no reg pip, then do pip conserve
        else:
            reg_pip = next((pip for pip in caster_player.pips if pip.school == "REG"), None)
            if reg_pip:
                caster_player.remove_pip(reg_pip)
            else:
                to_rem = caster_player.pips[0]
             #   print(f"To remove pip: {to_rem}")
                caster_player.remove_pip(to_rem)
             #   conserved = True
            #    if conserved:
             #       caster_player.pips.insert(0, Pip("REG"))
                #    print(f"After insertin reg: {caster_player.pips}")
            context.pips -= 1

        # for school, cost in context.schoolpips.items():
        #     print(f"here")
        #     while before_casting.get(school, 0) > 0 and cost > 0:
        #         print(f"{caster_player.name} eats {cost} {school} pip")
        #         before_casting[school] -= 1
        #         cost -= 1

        # then eats from regular pips
        # while before_casting.get("REG", 0) > 0:
        #     print(f"{before_casting["REG"]}")
        #     before_casting["REG"] -= 1
        #     context.pips -= 1
        #     print(f"{before_casting["REG"]}")
        
        # then eats from power pips
        # while before_casting.get("POWER", 0) > 0:
        #     before_casting["POWER"] -= 1
        #     context.pips -= 1

        # then eats from remaining school pips
        # for school, cost in before_casting.items():
        #     print(f"{school}: {cost}")
        #     if cost > 0:
        #         before_casting[school] -= 1
        #         print(f"before_casting[school] cost > 0: {before_casting[school]}")
        #         context.pips -= 2

        # if context.pips < 0:
        #     # do pip conserve stuff here!
        #     reg_pips = before_casting.get("REG", 0)
        #     reg_pips += 1
        #     before_casting["REG"] = reg_pips
        
        print(f"{context.pips} pips left to eat")
        print(f"Player has: {caster_player.pips}")

 #   caster_player.pips = { school: caster_player.pips.get(school, 0) - context.pips for school in caster_player.pips }
    caster_player.shadpips -= context.shadpips


    print(f"{caster_player.name} has {caster_player.pips} pips and {caster_player.shadpips} shad pips after casting")

  #  print(f"{caster_player.name} has {caster_player.pips} pips and {caster_player.shadpips} shad pips left")
# fire ice storm (traps/shields) -> put on order
# ice storm fire (blades) -> put on order
# cleanse charm removes fire weakness - ice/storm left
# pierce removes storm shield - fire/ice left

def cast_spell(match_obj, caster_player, enemy_player, spell_data):
    # if a player passes that turn, skip
    if spell_data in (None, "NONE"):
        return
    
    pipcost = spell_data.get("PIPCOST", 0)
    schoolpipcost = spell_data.get("SCHOOLPIPS", {})
    shadcost = spell_data.get("SHADCOST", 0)

    context = SpellInstance(spell_data, caster_player, enemy_player, pipcost, schoolpipcost, shadcost)

    print(f"{caster_player.name} pays {pipcost} pips, {schoolpipcost} school pips, and {shadcost} shad pips")

    handle_pips(caster_player, context)
    # loop through the effects of the spell
    # then apply them to the right player in match_obj
    for effect in context.spell["EFFECTS"]:
        effect_type = effect["TYPE"]

        print(f"Adding effect: {effect_type}")

        effect_class = Effect.registry[effect["TYPE"]]
        effect_obj = effect_class.from_json(effect)

        print(effect_obj)

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

                if effect_obj.type == "BACKLASH":
                    if abs_target.backlash is not None:
                        perc_dmg = caster_player.backlash.accumulated
                        dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
                        print(f"{caster_player.name} takes {dmg_taken} damage!")
                        caster_player.dec_health(dmg_taken)
                        print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
                    abs_target.backlash = effect_obj
                    continue
                
                for _ in range(amount):

                    new_effect = effect_obj.clone()

                    if new_effect.type == "DOT":
                        new_effect.get_damage(match_obj, caster_player, context)
                    abs_target.add_effect(new_effect)

            
            case "MATCH":
                match_obj.global_effect = effect_obj

            case None:
                effect_obj.apply(match_obj, caster_player, enemy_player, context)

      #  print(f"{effect_obj} has persistance: {effect_obj.is_persistant()}")
        # if effect_obj.is_persistant():
        #     abs_target = get_target(caster_player, enemy_player, effect)
        #     abs_target.add_effect(effect_obj)
        # else:
        #     effect_obj.apply(match_obj, caster_player, enemy_player)

    for charm, player in context.charms_used.items():
        print(f"Used charm: {charm}")
        player.del_effect(charm)

# match_obj is what is changing over time --
# "match" var just refers to the raw match json code

# this function starts the match by reading from the match file
# it uses match_obj to determine the parameters of the match
# (player info)
def start_match(match_obj):
    try:
        with open("../json_data/ezra_jason.json", "r") as f:
            match = json.load(f)
    except json.JSONDecodeError:
        print("ERROR! FAILED TO DECODE JSON!")

    try:
        with open("../json_data/spells.json") as f:
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
        # if round > 20:
        #     break
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

        # if caster == "PLAYER1":
        #     for effect in p1e1:
        #         effect.begin_round()
        #         if effect.expired():
        #             if effect.type == "BACKLASH":
        #                 perc_dmg = effect.accumulated
        #                 dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
        #                 print(f"{caster_player.name} takes {dmg_taken} damage!")
        #                 caster_player.dec_health(dmg_taken)
        #                 print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
        #             caster_player.del_effect(effect)
        # else:
        #     for effect in p2e1:
        #         effect.begin_round()
        #         if effect.expired():
        #             if effect.type == "BACKLASH":
        #                 perc_dmg = effect.accumulated
        #                 dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
        #                 print(f"{caster_player.name} takes {dmg_taken} damage!")
        #                 caster_player.dec_health(dmg_taken)
        #                 print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
        #             caster_player.del_effect(effect)

     #   caster_backlash = next( (effect for effect in caster_player.effects if isinstance(effect, Backlash)), None )

        # this is where backlash is taken
        if caster_player.backlash:
            if caster_player.backlash.expired():
                perc_dmg = caster_player.backlash.accumulated
                dmg_taken = caster_player.max_health * (perc_dmg * 0.01)
                print(f"{caster_player.name} takes {dmg_taken} damage!")
                caster_player.dec_health(dmg_taken)
                print(f"{caster_player.name} HEALTH: {math.floor(caster_player.curr_health)}")
                caster_player.backlash = None

        # this is where backlash eats
        print(f"caster_backlash: {caster_player.backlash}")
        if caster_player.backlash:
            eat_effect = caster_player.backlash.condition["EFFECT"]
            effect_target = caster_player.backlash.condition["TARGET"]

            if effect_target == "SELF":
                eat_target = caster_player
            elif effect_target == "ENEMY":
                eat_target = enemy_player
            
            ate = False

            print(f"eat_effect: {eat_effect}")
            for effect in reversed(eat_target.effects):
                if eat_effect in effect.categories:
                    eat_target.del_effect(effect)
                    print(f"eating effect: {effect} from {eat_target.name}")
                    ate = True
                    break

            if not ate:
                caster_player.backlash.inc_backlash()
                print("Did not eat an effect")

        # this is where DOTs activate
        caster_dots = [ effect for effect in caster_player.effects if isinstance(effect, DOT) ]

        for dot in caster_dots:
            print(f"DOT: {dot}")
            dot.tick(caster_player, match_obj)
            dot.begin_round()

        caster_bombs = [ effect for effect in caster_player.effects if isinstance(effect, Bomb_DOT) ]

        for dot in caster_bombs:
            print(f"DOT: {dot}")
            dot.begin_round()

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

        if caster_player.curr_health <= 0 or enemy_player.curr_health <= 0:
            match_obj.end_match(caster_player, enemy_player)
            break

        p1e2 = match_obj.getPlayer1().get_effects()
        p2e2 = match_obj.getPlayer2().get_effects()

        if caster == "PLAYER1":
            for effect in p1e2:
                effect.end_round()
        else:
            for effect in p2e2:
                effect.end_round()
        
        if caster_player.aura is not None:
        #    print("Caster aura:")
            caster_player.aura.end_round()
         #   print(caster_player.aura)
            if caster_player.aura.expired():
                caster_player.aura = None
        
        if enemy_player.aura is not None:
         #   print("Enemy aura:")
            print(enemy_player.aura)

        if caster_player.backlash is not None:
        #    print("Caster backlash:")
            caster_player.backlash.end_round()
        #    print(caster_player.backlash)
        
        if enemy_player.backlash is not None:
            pass
        #    print("Enemy backlash:")
        #    print(enemy_player.backlash)

        print_effects(match_obj.getPlayer1())
        print_effects(match_obj.getPlayer2())

        if turn.get("CONSERVE_PIP") in (None, "NONE"):
            conserved = None
         #   conserved = conservation_math()
        else:
            conserved = turn["CONSERVE_PIP"]
        
        if conserved:
            caster_player.pips.insert(0, Pip("REG"))

        school_pip = turn.get("SELECTED_SCHOOL")

      #  print(type(caster_player.pips))
      #  reg_idx = caster_player.pips.index("REG")

        # for pip in caster_player.pips:
        #     print(f"{pip}")

     #   reg_idx = next((i for i, pip in enumerate(caster_player.pips) if pip.school == "REG"), 0)

        reg_idx = caster_player.last_pip_index("REG")

        if reg_idx is None:
            caster_player.pips.insert(0, Pip(school_pip))
        else:        
            caster_player.pips.insert(reg_idx + 1, Pip(school_pip))

        print(f"Before sorting: {caster_player.pips}")

        caster_player.sort_pips()
        # caster_player.pips[reg_idx:]
        # caster_player.pips[school_pip] += 1
        print(caster_player.pips)

        if turn.get("GAIN_SHAD") == True:
            caster_player.shadpips += 1

        print(f"{caster_player.name} has {caster_player.shadpips} shadpips")

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
    with open("../json_data/players.json", "r") as f:
        players = json.load(f)
except json.JSONDecodeError:
    print("ERROR! FAILED TO DECODE JSON!")

try:
    with open("../json_data/matchups.json", "r") as f:
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