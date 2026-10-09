from .gamestate import GameState
from .spell_instance import SpellInstance
from .effects import Trap, Weakness, Heal_Weakness, Aura, Bubble, Pip
from .dataloader import *

class ReplayController:
    def __init__(self, player1, player2, match):
        self.p1 = player1
        self.p2 = player2

        self.match = match

    def insert_starting_conditions(self):
    #    print(f"start name: {self.p1.name}")
        if self.p1.name == "EZRA POLARKNIGHT":
            p1 = self.p1 # ezra
            p2 = self.p2 # jason

            self.bubble = Bubble("FIRE", 25)
            # self.change_bubble(Bubble("FIRE", 25))

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

    def play_match(self):
        if self.match.match_file:
            #   replay = ReplayController(self.p1, self.p2, self.spell_lookup)
            match_data = load_json(self.match.match_file)
            #   match_dat = self.load_json(self.match_file)
        spells = load_json("json_data/spells.json")
    #    spells = self.load_json("json_data/spells.json")

        spell_lookup = { spell["ID"]: spell for spell in spells }
        self.insert_starting_conditions()
        print(f"P1 HEALTH: {self.p1.curr_health}")
        print(f"P2 HEALTH: {self.p2.curr_health}")

        for turn in match_data:
            round = turn["ROUND"]
            if round > 30:
                break
            caster = turn["CASTER"]

            if caster == "PLAYER1":
                caster_player = self.p1
                enemy_player = self.p2
            elif caster == "PLAYER2":
                caster_player = self.p2
                enemy_player = self.p1

            print("----")

            # total_value = caster_player.calc_value()
            # print(f"Value of {caster_player.name}: {total_value}")
            # print(f"HP value of {caster_player.name}: {caster_player.hp_value}")
            # print(f"Pip value of {caster_player.name}: {caster_player.pip_value}")
            # print(f"Incoming value of {caster_player.name}: {caster_player.incoming_value}")
            # print(f"Outgoing value of {caster_player.name}: {caster_player.outgoing_value}")

            # total_value2 = enemy_player.calc_value()
            # print(f"Value of {enemy_player.name}: {total_value2}")
            # print(f"HP value of {enemy_player.name}: {enemy_player.hp_value}")
            # print(f"Pip value of {enemy_player.name}: {enemy_player.pip_value}")
            # print(f"Incoming value of {enemy_player.name}: {enemy_player.incoming_value}")
            # print(f"Outgoing value of {enemy_player.name}: {enemy_player.outgoing_value}")

            state = GameState(self.p1, self.p2)

            state.check_state()

            # this is where backlash is taken
            if caster_player.backlash:
                caster_player.take_backlash()

            # this is where backlash eats
            print(f"caster_backlash: {caster_player.backlash}")
            if caster_player.backlash:
                caster_player.backlash_eat(enemy_player)

            # this is where DOTs activate
            caster_player.activate_dots(self.match)

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

                context = SpellInstance(self.match, spell_data, caster_player, enemy_player, spell_data.get("PIPCOST"), spell_data.get("SCHOOLPIPS"), spell_data.get("SHADCOST"), multi=False)

                print(f"shad pips: {context.shadpips}")
                print(f"Caster pips: {caster_player.pips}")
                context.cast_spell(caster_player, enemy_player)

            # checks if a player has reached 0 health (end match)
            if caster_player.curr_health <= 0 or enemy_player.curr_health <= 0:
                self.match.end_match(caster_player, enemy_player)
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
            green = "\033[92m"
            reset = "\033[0m"
            print(f"{green}{caster_player.name} HEALTH: {caster_player.curr_health}{reset}")
            print(f"{green}{enemy_player.name} HEALTH: {enemy_player.curr_health}{reset}")