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
from match.match import Match
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

def test_single_damage(basic_match, make_spell, balance_player, storm_player):
    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell, balance_player, storm_player)

def test_blade(basic_match, make_spell, balance_player, storm_player):
    blade = Blade(
        school = "BALANCE",
        value = 35,
        family = "TESTBLADE35"
    )

    balance_player.add_effect(blade)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell, balance_player, storm_player)

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
    cast_spell(basic_match, spell, balance_player, storm_player)

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
    cast_spell(basic_match, spell, balance_player, storm_player)

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
    cast_spell(basic_match, spell, balance_player, storm_player)

def test_trap(basic_match, make_spell, balance_player, storm_player):
    trap = Trap(
        school = "BALANCE",
        value = 35,
        family = "TESTTRAP35"
    )

    storm_player.add_effect(trap)

    spell = make_spell("SUPERCRUSADE", balance_player, storm_player)
    cast_spell(basic_match, spell, balance_player, storm_player)

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
    cast_spell(basic_match, spell, balance_player, storm_player)

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
    cast_spell(basic_match, spell, balance_player, storm_player)

    storm_player.print_effects()
    balance_player.print_effects()

def test_clear_weakness(basic_match, make_spell, balance_player, storm_player):
    shield1 = Weakness(
        school = "UNIVERSAL",
        value = 50,
        family = "A"
    )
    shield2 = Weakness(
        school = "FIRE",
        value = 25,
        family = "B"
    )
    shield3 = Weakness(
        school = "FIRE",
        value = 25,
        family = "C"
    )

    balance_player.add_effect(shield1)
    balance_player.add_effect(shield2)
    balance_player.add_effect(shield3)

    spell = make_spell("EVILSNOWMAN_2B", balance_player, storm_player)
    cast_spell(basic_match, spell, balance_player, storm_player)

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

def test_multi_select(basic_match, make_spell, balance_player, storm_player):
    minion1 = Minion(
        id = "STORMELEMENTAL",
        duration = 7
    )
    
    storm_player.minion = minion1

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

    spell = make_spell("DROPBEARFURY_5B", balance_player, storm_player)

    storm_player.print_effects()

    cast_spell(basic_match, spell, balance_player, storm_player)
    # for effect in spell.spell["EFFECTS"]:
    #     effect_class = Effect.registry[effect["TYPE"]]
    #     effect_obj = effect_class.from_json(effect)
    #     print(effect_obj)
    #     if effect["TYPE"] == "DAMAGE":
    #         is_multi = spell.get("MULTI", None)
    #         if is_multi is not None:
    #             # put code here to determine how many user selected
    #             effect_obj.value = effect.value / 2
    #         basic_match.do_damage(spell.caster, spell.enemy, effect_obj, spell)
    #     elif effect["TYPE"] == "GAMBIT":
    #         basic_match.play_gambit(spell.caster, spell.enemy, effect_obj, spell)
    
    storm_player.print_effects()



def test_swap_many(basic_match, make_spell, balance_player, storm_player):
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

def test_multi_select_pip(basic_match, make_spell, balance_player, storm_player):
    minion1 = Minion(
        id = "STORMELEMENTAL",
        duration = 7
    )
    
    storm_player.minion = minion1

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

    spell = make_spell("POWERNOVA_5B", balance_player, storm_player, True)

    storm_player.print_effects()
    print(f"caster pips: {balance_player.pips}")

    cast_spell(basic_match, spell, balance_player, storm_player)

    storm_player.print_effects()
    print(f"caster pips: {balance_player.pips}")

def test_double_hit(basic_match, make_spell, balance_player, storm_player):
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
    shield7 = Shield(
        school = "MYTH",
        value = 10,
        family = "F"
    )

    storm_player.add_effect(shield1)
    storm_player.add_effect(shield2)
    storm_player.add_effect(shield3)
    storm_player.add_effect(shield4)
    storm_player.add_effect(shield5)
    storm_player.add_effect(shield6)

    spell = make_spell("MINOTAUR_2C", balance_player, storm_player, True)

    storm_player.print_effects()

    cast_spell(basic_match, spell, balance_player, storm_player)

    storm_player.print_effects()