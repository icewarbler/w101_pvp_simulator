# Architecture

## Overview

The Wizard101 PvP simulator models a complete Wizard101 battle using an object-oriented design structure.

The primary goals are:

- accurately reproduce in-game mechanics
- implement probabilistic formulas and algorithms to generate unique possibilities (ie pip conservation, accuracy, critical, block, etc)
- support AI decision making in the future

The simulator is divided into several independent components.

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

Stores all information about a combatant

Responsibilities:

- health
- pips
- deck
- hand
- effects
- stats
- aura
- backlash

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

Each spell contains one or more Effects.

Examples:

- damage
- DOT
- bomb DOT
- trap
- shield
- blade
- weakness
- aura
- backlash
- gambit

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

---

### JSON Database

Game data is stored separately from engine code, and gathered using dataloader.py


---


### Testing

The simulator uses pytest