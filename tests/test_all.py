import pytest
from match.player import Player
from match.effects import Single_Damage
from match.effects import Effect
from match.effects import Blade
from match.effects import Trap
from match.effects import Shield
from match.effects import Aura
from match.match import Match
from match.dataloader import load_json
from match.spell_instance import SpellInstance

@pytest.fixture
def make_spell():
    def _make_spell(spell_name, caster=None, target=None):
        spells = load_json("json_data/spells.json")

        spell_data = next(spell for spell in spells if spell["ID"] == spell_name)

        return SpellInstance(
            spell_data, 
            caster, 
            target,
            spell_data.get("PIPCOST", 0),
            spell_data.get("SCHOOLPIPS", {}),
            spell_data.get("SHADCOST", 0)
        )

    return _make_spell

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

def cast_spell(match, spell):
    for effect in spell.spell["EFFECTS"]:
        effect_class = Effect.registry[effect["TYPE"]]
        effect_obj = effect_class.from_json(effect)
        print(effect_obj)
        if effect["TYPE"] == "DAMAGE":
            match.do_damage(spell.caster, spell.enemy, effect_obj, spell)
        elif effect["TYPE"] == "GAMBIT":
            match.play_gambit(spell.caster, spell.enemy, effect_obj, spell)

def test_single_damage(basic_match, make_spell, balance_player, storm_player):
    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_blade(basic_match, make_spell, balance_player, storm_player):
    blade = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35"
    )

    balance_player.add_effect(blade)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_blade_same_families(basic_match, make_spell, balance_player, storm_player):
    blade1 = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35"
    )

    blade2 = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35"
    )

    balance_player.add_effect(blade1)
    balance_player.add_effect(blade2)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_blade_diff_families(basic_match, make_spell, balance_player, storm_player):
    blade1 = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35"
    )

    blade2 = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35_2"
    )

    balance_player.add_effect(blade1)
    balance_player.add_effect(blade2)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_blade_order(basic_match, make_spell, balance_player, storm_player):
    blade1 = Blade(
        school = "UNIVERSAL",
        value = 25,
        family = "TESTBLADE35"
    )

    blade2 = Blade(
        school = "DEATH",
        value = 35,
        family = "TESTBLADEDEATH35"
    )

    balance_player.add_effect(blade1)
    balance_player.add_effect(blade2)

    spell = make_spell("MAJORSCOURGE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_trap(basic_match, make_spell, balance_player, storm_player):
    trap = Trap(
        school = "BALANCE",
        value = 35,
        family = "TESTTRAP35"
    )

    storm_player.add_effect(trap)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell)

def test_echo_shields(basic_match, make_spell, balance_player, storm_player):
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

    spell = make_spell("HYDRA_2B", balance_player, storm_player)
    cast_spell(basic_match, spell)

    storm_player.print_effects()
    balance_player.print_effects()


def test_echo_traps(basic_match, make_spell, balance_player, storm_player):
    shield1 = Trap(
        school = "UNIVERSAL",
        value = 50,
        family = "A"
    )
    shield2 = Trap(
        school = "FIRE",
        value = 25,
        family = "B"
    )
    shield3 = Trap(
        school = "FIRE",
        value = 25,
        family = "C"
    )
    shield4 = Trap(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield5 = Trap(
        school = "STORM",
        value = 40,
        family = "D"
    )
    shield6 = Trap(
        school = "UNIVERSAL",
        value = 10,
        family = "E"
    )

    balance_player.add_effect(shield1)
    balance_player.add_effect(shield2)
    balance_player.add_effect(shield3)
    balance_player.add_effect(shield4)
    balance_player.add_effect(shield5)
    balance_player.add_effect(shield6)

    spell = make_spell("LOCUSTSWARM_2B", balance_player, storm_player)
    cast_spell(basic_match, spell)

    storm_player.print_effects()
    balance_player.print_effects()

def test_aura_duration(storm_player):
    adj = [{
        "TYPE": "SHIELD",
        "SCHOOL": "UNIVERSAL",
        "VALUE": 20
    }]

    auraa = Aura(
        duration = 3,
        adj = adj
    )

    storm_player.aura = auraa

    print(f"{storm_player.aura.duration}")

    storm_player.aura.end_round()
    print(f"{storm_player.aura.duration}")

    storm_player.aura.end_round()
    print(f"{storm_player.aura.duration}")

    if storm_player.aura.expired():
        storm_player.aura = None

    storm_player.aura.end_round()
    print(f"{storm_player.aura.duration}")

    if storm_player.aura.expired():
        storm_player.aura = None

    assert storm_player.aura == None
