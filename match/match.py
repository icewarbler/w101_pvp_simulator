import random
from .effects import Effect, Pip
from .deck import Deck, Hand
from .spell_instance import SpellInstance
from .gamestate import GameState
from .machinecontroller import MachineController
from .humancontroller import HumanController
from .replaycontroller import ReplayController
from .dataloader import *

class Match:
    def __init__(self, p1, p2, turn, match_file=None):
        self.p1 = p1
        self.p2 = p2
        self.turn = turn

        self.match_file = match_file

        self.global_effect = []

    def add_effect(self, target_obj, effect):
        target_obj.add_effect(effect)

    def do_tick(self, caster, dot):
        effect_value = dot.value_per_tick
        effect_school = dot.school
        pierce_val = dot.pierce_val

        effect_value = caster.mod_incoming_damage(effect_value, effect_school, pierce_val, True)

        caster.dec_health(effect_value)
        red = "\033[91m"
        reset = "\033[0m"
        print(f"{red}OWIE! DOT tick does {effect_value} damage!{reset}")
        print(f"{caster.name} HEALTH: {caster.curr_health}")

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

    def init_match(self):
        self.p1.pips.append(Pip("REG"))
        self.p1.pips.append(Pip("POWER"))
        self.p1.pips.append(Pip("POWER"))

        self.p1.shadpips = 1
        self.p2.shadpips = 2

        self.p2.pips.append(Pip("REG"))
        self.p2.pips.append(Pip("POWER"))
        self.p2.pips.append(Pip("POWER"))

    def start_match(self):
        if not self.match_file:
            turn = 0

            self.p1.deck = Deck(self.p1.deck)
          #  print(f"{self.p1.name} DECK:")
          #  print(self.p1.deck)
          #  print("----")


            for _ in range(Hand.max_cards):
                self.p1.draw_card()

            self.p2.deck = Deck(self.p2.deck)
            # print(f"{self.p2.name} DECK:")
            # print(self.p2.deck)
           # print("----")

            for _ in range(Hand.max_cards):
                self.p2.draw_card()

            spells = load_json("json_data/spells.json")
        #    spells = self.load_json("json_data/spells.json")

            spell_lookup = { spell["ID"]: spell for spell in spells }

            self.init_match()

            machine = MachineController(self.p1, self.p2, spell_lookup, self)

            human = HumanController(self.p1, self.p2, spell_lookup)

            state = GameState(self.p1, self.p2)

            # loop to do turn
            while True:
                if turn % 2 != 0:
                    while len(self.p2.hand.cards) < Hand.max_cards and len(self.p2.deck.cards):
                        self.p2.draw_card()
                    selected_spell = machine.choose_spell(state, self.p2.hand.cards)
                    print(f"selected seppl: {selected_spell}")
                    if selected_spell is None:
                        print(f"Round {turn}: {self.p2.name} PASSES")
                        turn += 1
                        continue
                    context = SpellInstance(self, selected_spell, self.p2, self.p1, selected_spell.get("PIPCOST"), selected_spell.get("SCHOOLPIPS"), selected_spell.get("SHADCOST"))
                    context.cast_spell(self.p2, self.p1)
                    turn += 1
                    continue


                caster_player = self.p1
                enemy_player = self.p2

                while len(self.p1.hand.cards) < Hand.max_cards and len(self.p1.deck.cards):
                 #   print(f"{caster_player.name} has {len(caster_player.hand.cards)} cards in hand!")
                    self.p1.draw_card()

                print("\n")
                print(f"{caster_player.name} HEALTH: {caster_player.curr_health} / {caster_player.max_health}")
                print("\n")
                print(f"{enemy_player.name} HEALTH: {enemy_player.curr_health} / {enemy_player.max_health}")
                print("\n")

                print(f"Your pips: {caster_player.pips}")

                print("\n")

                spell_id, spell_data = human.select_spell()

                if spell_id == 0:
                    print(f"**PASS")
                    print(f"Round {turn}: {caster_player.name} PASSES")

                if spell_id != 0:
                    print(f"**SPELL: {spell_id}")
                    # get data from that spell to add to match
                 #   spell_data = spell_lookup.get(spell_id)

                    print(f"Round {turn}: {caster_player.name} casts {spell_id}")

                    context = SpellInstance(self, spell_data, caster_player, enemy_player, spell_data.get("PIPCOST"), spell_data.get("SCHOOLPIPS"), spell_data.get("SHADCOST"))
                    context.cast_spell(caster_player, enemy_player)

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

        replay = ReplayController(self.p1, self.p2, self)

        replay.play_match()

    def end_match(self, caster_player, enemy_player):
        if caster_player.curr_health <= 0:
            print(f"{caster_player.name} has been defeated!")
        elif enemy_player.curr_health <= 0:
            print(f"{enemy_player.name} has been defeated!")