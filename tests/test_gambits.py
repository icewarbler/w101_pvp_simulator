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
from match.effects import DOT
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

# swaps shields
def test_hydra_c(basic_match, make_spell, balance_player, storm_player):
    storm_shields = [
        Shield("UNIVERSAL", 50, "A"),
        Shield("FIRE", 25, "B"),
        Shield("FIRE", 25, "C"),
        Shield("STORM", 40, "D"),
        Shield("STORM", 40, "D"),
        Shield("UNIVERSAL", 10, "E")
    ]

    for shield in storm_shields:
        storm_player.add_effect(shield)

    life_shield = Shield("LIFE", 50, "F")
    balance_player.add_effect(life_shield)

    balance_player.print_effects()
    storm_player.print_effects()

    spell = make_spell("HYDRA_5C", balance_player, storm_player)

    cast_spell(basic_match, spell, balance_player, storm_player)

    balance_player.print_effects()
    storm_player.print_effects()

# clears 4 shields for dots
def test_dropbear_b(basic_match, make_spell_data, balance_player, storm_player):
    storm_player.pips.append(Pip("REG"))
    storm_player.pips.append(Pip("REG"))
    storm_player.pips.append(Pip("REG"))

    minionn = make_spell_data("WATERELEMENTAL")

    basic_match.cast_spell(storm_player, storm_player, minionn)
    

    storm_shields = [
        Shield("UNIVERSAL", 50, "A"),
        Shield("FIRE", 25, "B"),
        Shield("FIRE", 25, "C"),
        Shield("STORM", 40, "D"),
        Shield("STORM", 40, "D"),
        Shield("UNIVERSAL", 10, "E")
    ]

    for shield in storm_shields:
        storm_player.add_effect(shield)

    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("FIRE"))

    spell = make_spell_data("DROPBEARFURY_5B")

    storm_player.print_effects()

    basic_match.cast_spell(balance_player, storm_player, spell)
    
    storm_player.print_effects()


# clears 5 weaknesses for bomb dots
def test_stonecolossus(basic_match, make_spell_data, balance_player, storm_player):
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))

    balance_weaknesses = [
        Weakness("UNIVERSAL", 50, "A"),
        Weakness("FIRE", 25, "B"),
        Weakness("FIRE", 25, "C"),
        Weakness("STORM", 40, "D"),
        Weakness("STORM", 40, "D"),
        Weakness("UNIVERSAL", 10, "E"),
        Weakness("MYTH", 10, "F")
    ]

    for effect in balance_weaknesses:
        balance_player.add_effect(effect)

    balance_player.print_effects()
    
    spell = make_spell_data("STONECOLOSSUS_5B")

    basic_match.cast_spell(balance_player, storm_player, spell)

    balance_player.print_effects()
    storm_player.print_effects()

    assert len(balance_player.effects) == 1, "Balance player should have 1 weakness remaining!"
    assert len(storm_player.effects) == 5, "Storm player should have 5 DOTs"

# echoes 4 dots
def test_chimera_b(basic_match, make_spell_data, balance_player, storm_player):
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))

    balance_dots = [
        DOT("FIRE", 3, 3, 150),
        DOT("FIRE", 3, 3, 150),
        DOT("FIRE", 3, 3, 150),
        DOT("FIRE", 3, 3, 150),
        DOT("FIRE", 3, 3, 150),
    ]

    for effect in balance_dots:
        balance_player.add_effect(effect)

    balance_player.print_effects()
    
    spell = make_spell_data("CHIMERA_5B")

    basic_match.cast_spell(balance_player, storm_player, spell)

    balance_player.print_effects()
    storm_player.print_effects()

# if_gambit (gambit self-aura and 3 traps on enemy)
def test_tribunaloni(basic_match, make_spell_data, balance_player, storm_player):
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))

    adj = [{
        "TYPE": "SHIELD",
        "SCHOOL": "UNIVERSAL",
        "VALUE": 20
    }]
    balance_player.aura = Aura(2, adj)

    if balance_player.aura:
        print(f"Balance player aura: {balance_player.aura}")

    storm_traps = [
        Trap("UNIVERSAL", 50, "A"),
        Trap("FIRE", 25, "B"),
        Trap("FIRE", 25, "C"),
        Trap("STORM", 40, "D"),
        Trap("STORM", 40, "D"),
        Trap("UNIVERSAL", 10, "E"),
        Trap("MYTH", 10, "F")
    ]

    for effect in storm_traps:
        storm_player.add_effect(effect)

    storm_player.print_effects()

    # storm player should have 2 fire traps
    # balance player should have no aura

    spell = make_spell_data("TRIBUNALONI")

    basic_match.cast_spell(balance_player, storm_player, spell)

    balance_player.print_effects()
    storm_player.print_effects()

    assert len(storm_player.effects) == 2, "Storm player should have 2 traps remaining!"
    assert not balance_player.aura, "Balance player should have no aura!"

    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))
    balance_player.pips.append(Pip("POWER"))

    spell = make_spell_data("TRIBUNALONI")

    basic_match.cast_spell(balance_player, storm_player, spell)

    balance_player.print_effects()
    storm_player.print_effects()

    assert len(storm_player.effects) == 2, "Storm player should have 2 traps remaining!"

# clears 5 shields for dots
def test_helephant_b(basic_match, make_spell_data, balance_player, storm_player):
    storm_shields = [
        Shield("ICE", 50, "F"),
        Shield("UNIVERSAL", 50, "A"),
        Shield("FIRE", 25, "B"),
        Shield("FIRE", 25, "C"),
        Shield("STORM", 40, "D"),
        Shield("STORM", 40, "D"),
        Shield("UNIVERSAL", 10, "E")
    ]

    for shield in storm_shields:
        storm_player.add_effect(shield)

    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("REG"))
    balance_player.pips.append(Pip("FIRE"))

    spell = make_spell_data("HELEPHANT_5B")

    storm_player.print_effects()

    basic_match.cast_spell(balance_player, storm_player, spell)

    storm_player.print_effects()

# echoes shields
def test_hydra_b(basic_match, make_spell, balance_player, storm_player):
    deleted_shield = Shield("STORM", 40, "D")

    storm_shields = [
        Shield("UNIVERSAL", 50, "A"),
        Shield("FIRE", 25, "B"),
        Shield("FIRE", 25, "C"),
        Shield("STORM", 40, "D"),
        deleted_shield,
        Shield("UNIVERSAL", 10, "E")
    ]

    for shield in storm_shields:
        storm_player.add_effect(shield)

    life_shield = Shield("LIFE", 50, "F")
    balance_player.add_effect(life_shield)
    
    balance_player.print_effects()
    storm_player.print_effects()

    spell = make_spell("HYDRA_2B", balance_player, storm_player)

    cast_spell(basic_match, spell, balance_player, storm_player)

    balance_player.print_effects()
    storm_player.print_effects()

    assert life_shield in balance_player.effects, "Balance player should have a life shield!"
    assert storm_shields[2] not in storm_player.effects
    assert len(balance_player.effects) == 2
    assert deleted_shield not in storm_player.effects, "Most recent storm shield should not be present!"