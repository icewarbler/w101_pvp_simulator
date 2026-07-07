import json

class Effect():
    registry = {}

    @classmethod
    def register(cls, effect_type):
        def decorator(subclass):
            cls.registry[effect_type] = subclass
            return subclass
        return decorator

    @classmethod
    def from_json(cls, effect):
        return cls.registry[effect["TYPE"]].from_json(effect)

    def __str__(self):
        return self.type

    def clone(self):
        pass

    type = None

    def begin_round(self):
        pass

    def end_round(self):
        pass

    def expired(self):
        return False


@Effect.register("BUBBLE")
class Bubble(Effect):
    type = "BUBBLE"

    categories = {"BUBBLE"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"])
    
    def __init__(
        self,
        school,
        value
    ):
        self.school = school
        self.value = value

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def store_at(self):
        return "MATCH"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

@Effect.register("SINGLE_DAMAGE")
class Single_Damage:
    type = "SINGLE_DAMAGE"

    categories = {"DAMAGE", "SINGLE_DAMAGE"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["TARGET"], effect["SCHOOL"], effect["VALUE"])
    
    def __init__(
            self,
            target,
            school,
            value
    ):
        self.target = target
        self.school = school
        self.value = value

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def store_at(self):
        return None
    
    def apply(self, match, caster, enemy, context):
        match.do_damage(caster, enemy, self, context)

@Effect.register("RANGE_DAMAGE")
class Range_Damage:
    type = "RANGE_DAMAGE"

    categories = {"DAMAGE", "RANGE_DAMAGE"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["TARGET"], effect["SCHOOL"], effect["MIN"], effect["MAX"])
    
    def __init__(self, target, school, min, max):
        self.target = target
        self.school = school
        self.min = min
        self.max = max

    def __str__(self):
        return f"{self.type}: {self.school} {self.min} {self.max}"

    def store_at(self):
        return None
    
    def apply(self, match, caster, enemy, context):
        match.do_damage(caster, enemy, self, context)


class Heal:
    def __init__(
            self,
            value
    ):
        self.value = value

class Charm(Effect):
    categories = {"CHARM"}

    def __init__(
            self,
            value,
            family
    ):
        self.value = value
        self.family = family

    def clone(self):
        return Charm(self.value, self.family)

    def begin_round(self):
        pass
    
    def end_round(self):
        pass

@Effect.register("BLADE")
class Blade(Charm):
    type = "BLADE"

    categories = {"CHARM", "BLADE"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(self, school, value, family):
        super().__init__(value, family)
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def clone(self):
        return Blade(self.school, self.value, self.family)
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 + self.value * 0.01)

@Effect.register("WEAKNESS")
class Weakness(Charm):
    type = "WEAKNESS"

    categories = {"CHARM", "WEAKNESS"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(self, school, value, family):
        super().__init__(value, family)
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def clone(self):
        return Weakness(self.school, self.value, self.family)
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 - self.value * 0.01)
    
@Effect.register("HEAL_WEAKNESS")
class Heal_Weakness(Charm):
    type = "HEAL_WEAKNESS"

    categories = {"CHARM", "WEAKNESS", "HEAL_WEAKNESS"}

    @classmethod
    def from_json(cls, effect):
        return cls( effect["VALUE"], effect["FAMILY"])
    
    def __init__(self, value, family):
        super().__init__(value, family)

    def __str__(self):
        return f"{self.type}: {self.value}"
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        pass


class Ward(Effect):
    categories = {"WARD"}

    def __init__(
            self,
            school,
            value,
            family
    ):
        self.school = school
        self.value = value

        self.family = family

    def clone(self):
        return Ward(self.school, self.value, self.family)

    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        pass

@Effect.register("DOT_TRAP")
class DOT_Trap(Ward):
    type = "DOT_TRAP"

    categories = {"WARD", "TRAP", "DOT_TRAP"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(
        self,
        school,
        value,
        family
    ):
        super().__init__(school, value, family)

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def clone(self):
        return DOT_Trap(self.school, self.value, self.family)
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage, pierce):
        return pierce, damage * (1 + self.value * 0.01)

@Effect.register("TRAP")
class Trap(Ward):
    type = "TRAP"

    categories = {"WARD", "TRAP"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(
        self,
        school,
        value,
        family
    ):
        super().__init__(school, value, family)

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def clone(self):
        return Trap(self.school, self.value, self.family)
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage, pierce):
        return pierce, damage * (1 + self.value * 0.01)

@Effect.register("SHIELD")
class Shield(Ward):
    type = "SHIELD"

    categories = {"WARD", "SHIELD"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(
        self,
        school,
        value,
        family
    ):
        super().__init__(school, value, family)

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def clone(self):
        return Shield(self.school, self.value, self.family)
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage, pierce):
        mod_val = self.value
        mod_val -= pierce
        if mod_val < 0:
            pierce = -(mod_val)
            mod_val = 0
        else:
            pierce = 0
        print(f"shield val after pierce: {mod_val}; pierce: {pierce}")
        return pierce, damage * (1 - mod_val * 0.01)

#Your gear (% then flat)-> 
# your aura -> 
# your charms-> 
# the global-> 
# target's aura->
# target's wards-> 
# target's gear(flat then %)-> 
# critical 

# self aura:
# increase outgoing dmg (increase self damage)- pos charm
# decrease incoming damage (increase self resistance) - pos ward
# increase incoming damage (decrease self resist) - neg ward
# increase stun res / increase crit block

# de-aura:
# increase incoming damage (decrease enemy res) - neg ward
# decrease outgoing damage (decrease enemy damage) - neg charm
@Effect.register("AURA")
class Aura(Effect):
    type = "AURA"

    categories = {"AURA"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["DURATION"], effect["ADJ"])
    
    def __init__(
        self,
        duration,
        adj
        # the effects are just charms/wards
    ):
        self.duration = duration
        self.adj = adj

    def __str__(self):
        effects = ", ".join(str(e) for e in self.adj)
        return f"{self.type} ({self.duration} turns): {effects}"
       # return f"{self.type}: {self.duration} { {effect.get("TYPE"): effect.get("VALUE") for effect in self.adj} }"

    def clone(self):
        return Aura(self.duration, self.adj)
    
    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        self.duration -= 1

    def expired(self):
        return self.duration <= 0

# decreases health
@Effect.register("DOT")
class DOT(Effect):
    type = "DOT"

    categories = {"DOT"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["DURATION"], effect["AMOUNT"], effect["VALUE_PER_STACK"])
        
    def __init__(
            self,
            school,
            duration,
            stacks,
            value
    ):
        self.school = school
        self.duration = duration
        self.stacks = stacks
        self.value = value

        self.value_per_tick = 0
        self.leftover_value = value

        self.pierce_val = 0

    def __str__(self):
        return f"{self.type}: {self.school} {self.duration} {self.value_per_tick} / {self.value}"
    
    def clone(self):
        return DOT(self.school, self.duration, self.stacks, self.value)

    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        self.duration -= 1

    def end_round(self):
        pass

    def get_damage(self, match, caster, context):
        match.dot_damage(caster, self, context)

    def new_damage(self, value):
        self.value = value
        self.leftover_value = value

    def new_tick_damage(self, value):
        self.value_per_tick = value

    def tick(self, caster, match):
        match.do_tick(caster, self)
        print(f"{self.leftover_value}")
        self.leftover_value -= self.value_per_tick
        print(f"{caster.name} took {self.value_per_tick} damage from dot; leftover: {self.leftover_value}")

    def set_pierce(self, value):
        self.pierce_val = value

@Effect.register("BOMB_DOT")
class Bomb_DOT(Effect):
    type = "BOMB_DOT"

    categories = {"DOT", "BOMB_DOT"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["DURATION"], effect["AMOUNT"], effect["VALUE_PER_STACK"])
        
    def __init__(
            self,
            school,
            duration,
            stacks,
            value
    ):
        self.school = school
        self.duration = duration
        self.stacks = stacks
        self.value = value

        self.pierce_val = 0

    def __str__(self):
        return f"{self.type}: {self.school} {self.duration} {self.value}"
    
    def clone(self):
        return Bomb_DOT(self.school, self.duration, self.stacks, self.value)

    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        self.duration -= 1

    def end_round(self):
        pass

    def get_damage(self, match, caster, context):
        match.dot_damage(caster, self, context)

    def new_damage(self, value):
        self.value = value

    def set_pierce(self, value):
        self.pierce_val = value


# increases health
@Effect.register("HOT")
class HOT(Effect):
    type = "HOT"

    categories = {"HOT"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["DURATION"], effect["AMOUNT"], effect["VALUE_PER_STACK"])

    def __init__(
            self,
            duration,
            stacks,
            value
    ):
        self.duration = duration
        self.stacks = stacks
        self.value = value

    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        self.duration -= 1

@Effect.register("BACKLASH")
class Backlash(Effect):
    type = "BACKLASH"

    categories = {"BACKLASH"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["DURATION"], effect["VALUE_PER_TURN"], effect["CONDITION"])
    
    def __init__(
            self,
            duration,
            value_per_turn,
            condition
    ):
        super().__init__()
        self.school = "SHADOW"
        self.duration = duration
        self.value_per_turn = value_per_turn
        self.condition = condition

        self.curr_turn = 0
        self.accumulated = value_per_turn

    def __str__(self):
        return f"{self.type}: {self.accumulated} {self.duration}"
    
    def clone(self):
        return Backlash(self.duration, self.value_per_turn, self.condition)
    
    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        self.curr_turn += 1
        self.duration -= 1
    
    def inc_backlash(self):
        self.accumulated += self.value_per_turn

    def expired(self):
        return self.duration <= 1

@Effect.register("GAMBIT")
class Gambit(Effect):
    type = "GAMBIT"

    categories = {"GAMBIT"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["CAUSE"], effect["PER_EFFECT"])
    
    def __init__(self, cause, per_effect):
        self.cause = cause
        self.per_effect = per_effect

    def __str__(self):
        return f"{self.type}"
    
    def store_at(self):
        return None

    def apply(self, match, caster, enemy, context):
        match.play_gambit(caster, enemy, self, context)

@Effect.register("MINION")
class Minion(Effect):
    type = "MINION"

    categories = {"MINION"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["ID"], effect["DURATION"])
    
    def __init__(self, id, duration):
        self.id = id
        self.duration = duration

        self.deck = []
        self.effects = []

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
        try:
            with open("../json_data/minion_spells.json") as f:
                spells = json.load(f)
        except json.JSONDecodeError:
            print("ERROR! FAILED TO DECODE JSON!")

        # puts every entry read from w101_spells.json into a dict
        spell_lookup = { spell["ID"]: spell for spell in spells }

        spell = spell_lookup[spell_id]
        
        return spell
    
    def add_effect(self, effect):
        self.effects.append(effect)