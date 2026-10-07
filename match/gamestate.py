# this is the state of the match at each turn
# it changes after a spell is used

class GameState:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def check_state(self):
        print(self.player1.hp_value)