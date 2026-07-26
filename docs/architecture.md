# Architecture

## Overview

The Wizard101 PvP simulator models a complete Wizard101 battle using an object-oriented design structure.

The primary goals are:

- accurately reproduce in-game mechanics
- implement probabilistic formulas and algorithms to generate unique possibilities (ie pip conservation, accuracy, critical, block, etc)
- support AI decision making in the future

The simulator is divided into several independent components, which are explained here.

---

## High-Level Architecture

```
               Match
                 |
    +------------------------+
    |                        |
  Player --- Minion       Player --- Minion
    |           |            |          |
   Deck/Hand    |       Deck/Hand       |
    |           |            |          |
    +-----------Spell--------+----------+
                  |
            Effect Resolution
```

---

## Core Components

### Match

Responsible for:

- turn order
- combat loop
- win conditions
- spell execution

The Match object owns the overall state of the battle

---

### Player

Stores all information about a combatant.

Responsibilities:

- health
- pips
- deck
- hand
- effects
- stats
- aura
- backlash
- minion

Players contain state but very little combat logic.

---

### Spell Instance

A spell instance represents one castable spell, loaded from a json file.

Example:
```json
{
    "ID": "BALANCEBLADE_25",
    "SPELL": "BALANCE BLADE",
    "SCHOOL": "BALANCE",
    "PIPCOST": 0,
    "ACCURACY": 100,
    "TYPE": ["CHARM", "BLADE"],
    "DESCRIPTION":
        "APPLIES A +25% DAMAGE BLADE",
    "EFFECTS": [
        {
            "TYPE": "BLADE",
            "TARGET": "SELF",
            "SCHOOL": "UNIVERSAL",
            "VALUE": 25,
            "FAMILY": "BALANCEBLADE_25"
        }
    ]
}
```

This allows hundreds of spells to share the same combat engine.

---

### Effects

Each spell contains one or more Effects, which are stored either in the `Match` object or `Player` object after being cast.

There are a bunch of effects, including:

- bubble
- single_damage
- range_damage
- percent_damage
- heal
- charm
- blade
- weakness
- heal_weakness
- ward
- trap
- DOT_trap
- shield
- aura
- DOT
- bomb DOT
- HOT
- backlash
- gambit
- if_gambit
- minion
- pip

Each Effect class implements only the logic needed for that effect type. The spell engine processes these effects sequentially.

---


### Pips

Pips (energy it costs to cast spells) are implemented as an Effect in effects.py:

```python
@Effect.register("PIP")
class Pip():
    type = "PIP"

    categories = {"PIP"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"])
    
    def __init__(self, school):
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school}"
    
    def __repr__(self):
        return str(self)
    
    def clone(self):
        return Pip(self.school)
    
    def store_at(self):
        return "PLAYER"
```

Pips are implemented as effects because they are easily manipulated by spells. Each `player` object contains an array of `pip` objects so that the player may only cast a valid spell when they have enough pips.

School/archmastery pips are generated each round according to the player's selected school. 

---

### Minions

Similar to pips, minions are also implemented as an Effect object:

```python
@Effect.register("MINION")
class Minion(Effect):
    type = "MINION"

    categories = {"MINION"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["ID"], 
                   effect["NAME"], 
                   effect["RANK"], 
                   effect["HEALTH"], 
                   effect["SCHOOL"],
                   effect["DURATION"],
                   effect["OUTGOING_DAMAGE"],
                   effect["INCOMING_RESIST"],
                   effect["PIERCE"],
                   effect["DECK"]
                   )
    
    def __init__(self, id, name, rank, max_health, school, duration, damage, resist, pierce, deck):
        self.id = id
        self.duration = duration

        self.name = name
        self.school = school

        self.rank = rank

        self.max_health = max_health

        self.curr_health = max_health

        self.outgoing_damage = damage
        self.incoming_resist = resist
        self.pierce = pierce

        self.deck = deck
        self.hand = Hand()

        self.pips = []
        self.shadpips = 0

        self.selected_school = school

        self.effects = []

        self.aura = None

        self.backlash = None

    def __str__(self):
        return self.type

    def clone(self):
        pass

    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        pass

    def expired(self):
        return False
    
    def cast_spell(self, spell_id):
        spells = load_json("json_data/minion_spells.json")

        spell_lookup = { spell["ID"]: spell for spell in spells }

        spell = spell_lookup[spell_id]
        
        return spell
```

Each player may have at most one minion, which is stored within the `Player` object itself.

---

### Gambits

There are 2 types of gambits: typical gambits (`gambit`) and if-gambits (`if_gambit`). Typical gambits simply apply an effect per an effect on the field already; if-gambit analyze the current effects on the field, and activate only if certain conditions are met.

For example, this is the `if_gambit` for `tribunal_oni`, which does more damage if and only if the there is an aura on the caster and at least 3 traps on the enemy:

```json
"TYPE": "IF_GAMBIT",
"CAUSE": [
    {
        "ACTION": "GAMBIT",
        "TARGET": "SELF",
        "TYPE": "AURA",
        "AMOUNT": 1
    },
    {
        "ACTION": "GAMBIT",
        "TARGET": "ENEMY",
        "TYPE": "TRAP",
        "AMOUNT": 3
    }
],
"THEN": [
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "BALANCE",
        "VALUE": 545
    },
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "STORM",
        "VALUE": 545
    },
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "MYTH",
        "VALUE": 545
    }
],
"ELSE": [
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "BALANCE",
        "VALUE": 245
    },
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "STORM",
        "VALUE": 245
    },
    {
        "TYPE": "SINGLE_DAMAGE",
        "TARGET": "ENEMY",
        "SCHOOL": "MYTH",
        "VALUE": 245
    }
```

In contrast, this is the typical `gambit` effect in `banshee_2c`, which clears at most 2 enemy blades and, for each, applies a -25% weakness on the enemy:

```json
"TYPE": "GAMBIT",
"CAUSE": [
    {
        "ACTION": "CLEAR",
        "TARGET": "ENEMY",
        "TYPE": "BLADE",
        "MAX": 2
    }
],
"PER_EFFECT": {
    "TARGET": "ENEMY",
    "TYPE": "WEAKNESS",
    "SCHOOL": "UNIVERSAL",
    "VALUE": 25,
    "FAMILY": "BANSHEE_25"
}
```

Each `gambit` has an action associated with it that tells what to do with the current effect on the field. They are as follows:

- CLEAR: removes a harmful effect from the field
- GAMBIT: removes a helpful effect from the field
- ECHO: copies a targets helpful effect
- SWAP: swaps an effect of a certain type with the target
- STEAL: takes a target's helpful effect and moves it to the caster
- PUSH: moves a harmful effect from the caster to the target (typically used to get rid of a DOT)
- EXTEND: extends the active time of a helpful effect (typically used to increase the ticks of a DOT)
- DETONATE: explodes a DOT effect on the target for a percentage of its total remaining damage

---

### JSON Database

Game data is stored separately from engine code, and gathered using dataloader.py

matchups.json → pre-defined matches to initialize from a json file

players.json → all possible players and their stats

spells.json → all the possible spells a player may cast

minions.json → all the possible minions

minion_spells.json → all the possible spells a minion may cast


---


### Testing

The simulator uses pytest, in the /tests folder. To run all tests, run with `test_all`; to just run gambits, run with `test_gambits`