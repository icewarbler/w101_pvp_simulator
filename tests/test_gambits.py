import pytest
from match.player import Player
from match.effects import Single_Damage
from match.effects import Effect
from match.effects import Blade
from match.effects import Trap
from match.effects import Shield
from match.effects import Aura
from match.effects import Weakness
from match.effects import Minion
from match.effects import Pip
from match.match import Match
import match.match
from match.dataloader import load_json
from match.spell_instance import SpellInstance

@pytest.fixture
def make_spell():
    def _make_spell(spell_name, caster=None, target=None, multi=False):
        spells = load_json("json_data/spells.json")

        spell_data = next(spell for spell in spells if spell["ID"] == spell_name)

        return SpellInstance(
            spell_data, 
            caster, 
            target,
            spell_data.get("PIPCOST", 0),
            spell_data.get("SCHOOLPIPS", {}),
            spell_data.get("SHADCOST", 0),
            multi
        )

    return _make_spell

@pytest.fixture
def make_spell_data():
    def _make_spell_data(spell_name):
        spells = load_json("json_data/spells.json")

        spell_data = next(spell for spell in spells if spell["ID"] == spell_name)

        return spell_data

    return _make_spell_data

@pytest.fixture
def balance_player():
    return Player(
        "BALANCE PLAYER",
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

@pytest.fixture
def storm_player():
    return Player(
        "STORM PLAYER",
        "STORM",
        "DEATH",
        180,
        9000,
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

@pytest.fixture
def basic_match(balance_player, storm_player):
    return Match(balance_player, storm_player, 0, None)

def cast_spell(basic_match, spell, caster_player, enemy_player):
    for effect in spell.spell["EFFECTS"]:
        effect_class = Effect.registry[effect["TYPE"]]
        effect_obj = effect_class.from_json(effect)
        if hasattr(effect_obj, "school"):
            if effect_obj.school == "ENEMY_SCHOOL":
                effect_obj.school = enemy_player.school
            elif effect_obj.school == "ALLY_SCHOOL":
                effect_obj.school = caster_player.school
        print(effect_obj)
        if effect["TYPE"] == "SINGLE_DAMAGE":
            if spell.multi:
                # put code here to determine how many user selected
                effect_obj.value = effect_obj.value / 2
            basic_match.do_damage(spell.caster, spell.enemy, effect_obj, spell)
        elif effect["TYPE"] == "GAMBIT":
            basic_match.play_gambit(spell.caster, spell.enemy, effect_obj, spell)

def test_hydra_c(basic_match, make_spell, balance_player, storm_player):
    shield1 = Shield(
        school = "UNIVERSAL",
        value = 50,
        family = "A"
    )
    shield2 = Shield(
        school = "FIRE",
        value = 25,
        family = "B"
    )
    shield3 = Shield(
        school = "FIRE",
        value = 25,
        family = "C"
    )
    shield4 = Shield(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield5 = Shield(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield6 = Shield(
        school = "UNIVERSAL",
        value = 10,
        family = "E"
    )

    storm_player.add_effect(shield1)
    storm_player.add_effect(shield2)
    storm_player.add_effect(shield3)
    storm_player.add_effect(shield4)
    storm_player.add_effect(shield5)
    storm_player.add_effect(shield6)

    shield7 = Shield(
        school = "LIFE",
        value = 50,
        family = "F"
    )

    balance_player.add_effect(shield7)

    balance_player.print_effects()
    storm_player.print_effects()

    spell = make_spell("HYDRA_5C", balance_player, storm_player)

    cast_spell(basic_match, spell, balance_player, storm_player)

    balance_player.print_effects()
    storm_player.print_effects()

def test_dropbear_b(basic_match, make_spell_data, balance_player, storm_player):
    storm_player.pips.append(Pip("REG"))
    storm_player.pips.append(Pip("REG"))
    storm_player.pips.append(Pip("REG"))

    minionn = make_spell_data("WATERELEMENTAL")

    basic_match.cast_spell(storm_player, storm_player, minionn)
    
 #   storm_player.minion = minion1

    shield1 = Shield(
        school = "UNIVERSAL",
        value = 50,
        family = "A"
    )
    shield2 = Shield(
        school = "FIRE",
        value = 25,
        family = "B"
    )
    shield3 = Shield(
        school = "FIRE",
        value = 25,
        family = "C"
    )
    shield4 = Shield(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield5 = Shield(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield6 = Shield(
        school = "UNIVERSAL",
        value = 10,
        family = "E"
    )

    storm_player.add_effect(shield1)
    storm_player.add_effect(shield2)
    storm_player.add_effect(shield3)
    storm_player.add_effect(shield4)
    storm_player.add_effect(shield5)
    storm_player.add_effect(shield6)

    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("FIRE"))

    spell = make_spell_data("DROPBEARFURY_5B")

    storm_player.print_effects()

    basic_match.cast_spell(balance_player, storm_player, spell)
    
    storm_player.print_effects()