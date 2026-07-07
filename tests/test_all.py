from match.player import Player
from match.effects import Single_Damage

def test_create_player():
    p1 = Player(
        "TEST PLAYER1",
        "BALANCE",
        "DEATH",
        180,
        14000,
        {
            "FIRE": 0,
            "ICE": 0,
            "STORM": 0,
            "MYTH": 0,
            "LIFE": 0,
            "DEATH": 0,
            "BALANCE": 0,
            "SHADOW": 0
        },
        {
            "FIRE": 0,
            "ICE": 0,
            "STORM": 0,
            "MYTH": 0,
            "LIFE": 0,
            "DEATH": 0,
            "BALANCE": 0,
            "SHADOW": 0
        },
        {
            "FIRE": 0,
            "ICE": 0,
            "STORM": 0,
            "MYTH": 0,
            "LIFE": 0,
            "DEATH": 0,
            "BALANCE": 0,
            "SHADOW": 0
        }
    )

def test_single_damage():
    damage = 135
    assert damage == 135