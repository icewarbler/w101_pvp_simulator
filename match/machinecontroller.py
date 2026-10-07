from .gamestate import GameState

# machine is always player 2
class MachineController:
    def __init__(self, player1, player2, spell_lookup):
        self.me = player1
        self.enemy = player2

        self.spell_lookup = spell_lookup
        
    def choose_spell(self, gamestate, cards):
        self.state = gamestate
        self.hand = cards

        max_pipcost = -1

        selected_spell = None

        for i, card in enumerate(cards):
            red = "\033[91m"
            reset = "\033[0m"

            spell = self.spell_lookup.get(card)

            if self.me.can_cast(spell):
                print(f"{i + 1}. {card}")
                # calculate the value of each spell
                # this is determined by the effects on the field, the school
                # of the players, and the value of each spell effect, per pip

                # damage is divided by the number of pips
                pipcost = spell.get("PIPCOST")
        
                school_pipcost = spell.get("SCHOOLPIPS")
                print(f"pipcs: {pipcost}, spc: {school_pipcost}")

                for key, item in school_pipcost.items() if school_pipcost else []:
                    print(f"{key}: {item}")
                    pipcost += int(item*2)
                    print(f"pipc new: {pipcost}")

                if pipcost > max_pipcost:
                    max_pipcost = pipcost
                    selected_spell = spell

                types = spell.get("TYPE")
                print(f"type: {types}")

                if "DAMAGE" in types:
                    effects = spell.get("EFFECTS")
                    
                    total_damage = 0

                    for effect in effects:
                        if effect.get("TYPE") == "SINGLE_DAMAGE":
                            damage_value = effect.get("VALUE")
                            total_damage += damage_value

                    print(f"damage: {total_damage}")

                    # calculate the value of the spell based on the damage and pip cost
                    value = total_damage / pipcost
                    print(f"value: {value}")


                # spell.calc_value()
            else:
                print(f"{i + 1}. {red}{card}{reset}")

                pipcost = spell.get("PIPCOST")
                school_pipcost = spell.get("SCHOOLPIPS")
                print(f"pipcs: {pipcost}, spc: {school_pipcost}")


                for key, item in school_pipcost.items() if school_pipcost else []:
                    print(f"{key}: {item}") 
                    pipcost += int(item*2)
                    print(f"pipc new: {pipcost}")

                types = spell.get("TYPE")
                print(f"type: {types}")

                if "DAMAGE" in types:
                    effects = spell.get("EFFECTS")

                    total_damage = 0

                    for effect in effects:
                        if effect.get("TYPE") == "SINGLE_DAMAGE":
                            damage_value = effect.get("VALUE")
                            total_damage += damage_value

                    print(f"damage: {total_damage}")

                    # calculate the value of the spell based on the damage and pip cost
                    value = total_damage / pipcost
                    print(f"value: {value}")

        print(f"selected spell: {selected_spell}")
        print(f"selected spell: {selected_spell.get('ID') if selected_spell else None}")

        return selected_spell