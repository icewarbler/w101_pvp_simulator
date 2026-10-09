from .spell_instance import SpellInstance

# machine is always player 2
class MachineController:
    def __init__(self, player1, player2, spell_lookup, match):
        self.me = player2
        self.enemy = player1
        self.match = match

        self.spell_lookup = spell_lookup
        
    def choose_spell(self, gamestate, cards):
        self.state = gamestate
        self.hand = cards

        self.state.check_state()

        max_pipcost = -1

        selected_spell = None

        for i, card in enumerate(cards):
            red = "\033[91m"
            reset = "\033[0m"

            spell = self.spell_lookup.get(card)

            pipcost = spell.get("PIPCOST")
                                    
            school_pipcost = spell.get("SCHOOLPIPS")
            shad_pipcost = spell.get("SHADCOST")
            spell_instance = SpellInstance(self.match, spell, self.me, self.enemy, pipcost, school_pipcost, shad_pipcost)

            spell_value = spell_instance.spell_value()

            if self.me.can_cast(spell):
                print(f"{i + 1}. {card}")

                spell_value = spell_instance.spell_value()

                selected_spell = spell
            else:
                print(f"{i + 1}. {red}{card}{reset}")

                spell_value = spell_instance.spell_value()

        print(f"selected spell: {selected_spell}")
        print(f"selected spell: {selected_spell.get('ID') if selected_spell else None}")

        return selected_spell