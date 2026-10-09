# this is the state of the match at each turn
# it changes after a spell is used

class GameState:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def check_state(self):
        print(self.player1.hp_value)

        p1_val = self.player1.calc_value()
        p2_val = self.player2.calc_value()

        print(f"Player 1 value: {p1_val}")
        print(f"Player 2 value: {p2_val}")