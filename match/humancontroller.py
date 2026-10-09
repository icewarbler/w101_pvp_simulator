import re

# human is always player1
class HumanController:
    def __init__(self, player1, player2, spell_lookup):
        self.me = player1
        self.enemy = player2

        self.spell_lookup = spell_lookup

    def parse_input(self):
        selection = input("> ").strip().lower()

        if selection == "info":
            print("OPTIONS:")
            print(f"[1-7] - Choose a spell to cast")
            print(f"d[1-7] - Delete a spell from your hand")
            print(f"i[1-7] - Print out the info for a spell")
            print(f"cs - Change the selected archmastery pip")
            print(f"ss - Print the currently selected archmastery pip")
            print(f"ee - Print the enemy's current effects")
            print(f"me - Print your current effects")
            print(f"health - Print the current health of both you and the enemy")
            print(f"pips - Print out your current pips")
            return 0

        if selection in ("p", "pass"):
            return None

        if re.match(r'^d[1-7]$', selection):
            #  print(f"selection: {selection}")
            if 1 <= int(selection[1:]) <= len(self.me.hand.cards):
                spell_id = self.me.hand.cards[int(selection[1:]) - 1]
                print(spell_id)
                self.me.delete_card(spell_id)
                return 0

        if re.match(r'^i[1-7]$', selection):
            #   print(f"selection: {selection}")
            if 1 <= int(selection[1:]) <= len(self.me.hand.cards):
                spell_id = self.me.hand.cards[int(selection[1:]) - 1]
                print(spell_id)
                spell_data = self.spell_lookup.get(spell_id)
                print(f"{spell_data.get("DESCRIPTION")}")
                return 0

        if selection == "health":
            print(f"Your Health: {self.me.curr_health}")
            print(f"Enemy Health: {self.enemy.curr_health}")
            return 0

        if selection == "pips":
            print(f"Your pips: {self.me.pips}")
            return 0
        
        if selection == "ee":
            if self.enemy.aura:
                print(self.enemy.aura)
            if self.enemy.backlash:
                print(self.enemy.backlash)
            print(self.enemy.print_effects())

        if selection == "me":
            if self.me.aura:
                print(self.me.aura)
            if self.me.backlash:
                print(self.me.backlash)
            print(self.me.print_effects())
        
        if selection == "cs":
            schools = [
                "FIRE",
                "ICE",
                "STORM",
                "LIFE",
                "DEATH",
                "MYTH",
                "BALANCE"
            ]

            print("Generate which archmastery pip?")

            for i, school in enumerate(schools):
                print(f"{i + 1}. {school}")

            while True:
                try:
                    school_selection = int(input("> "))
                except ValueError:
                    continue

                if 1 <= school_selection <= len(schools):
                    break

            self.me.selected_school = schools[school_selection - 1]

        if selection == "ss":
            print(f"Currently generating a {self.me.selected_school} pip")
        
        try:
            selection = int(selection)
        except ValueError:
            return 0

        if 1 <= selection <= len(self.me.hand.cards):
            spell_id = self.me.hand.cards[selection - 1]
            return spell_id

    def select_spell(self):
        while True:
            red = "\033[91m"
            reset = "\033[0m"
            print("SELECT A SPELL")
            for i, card in enumerate(self.me.hand.cards):
                spell = self.spell_lookup[card]

                if self.me.can_cast(spell):
                    print(f"{i + 1}. {card}")
                else:
                    print(f"{i + 1}. {red}{card}{reset}")

            spell_id = self.parse_input()
            spell_data = self.spell_lookup.get(spell_id)
            if spell_id != None and self.me.can_cast(spell_data):
                return spell_id, spell_data
            else:
                return 0, 0