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
        return None
    
    def apply(self, match, caster, enemy, effect):
        match.do_damage(caster, enemy, effect)

@Effect.register("RANGE_DAMAGE")
class Range_Damage:
    type = "RANGE_DAMAGE"

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["MIN"], effect["MAX"])
    
    def __init__(self, school, min, max):
        self.school = school
        self.min = min
        self.max = max

    def __str__(self):
        return f"{self.type}: {self.school} {self.min} {self.max}"

    def store_at(self):
        return None
    
    def apply(self, match, caster, enemy, effect):
        match.do_damage(caster, enemy, effect)


class Heal:
    def __init__(
            self,
            value
    ):
        self.value = value

class Charm(Effect):
    def __init__(
            self,
            value,
            family
    ):
        self.value = value
        self.family = family

    def begin_round(self):
        pass
    
    def end_round(self):
        pass

@Effect.register("BLADE")
class Blade(Charm):
    type = "BLADE"

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(self, school, value, family):
        super().__init__(value, family)
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
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

    @classmethod
    def from_json(cls, effect):
        return cls(effect["SCHOOL"], effect["VALUE"], effect["FAMILY"])
    
    def __init__(self, school, value, family):
        super().__init__(value, family)
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
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
    type = "WEAKNESS"

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
    def __init__(
            self,
            school,
            value,
            family
    ):
        self.school = school
        self.value = value

        self.family = family

    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        pass

@Effect.register("DOT_TRAP")
class DOT_Trap(Ward):
    type = "DOT_TRAP"

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
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 + self.value * 0.01)

@Effect.register("TRAP")
class Trap(Ward):
    type = "TRAP"

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
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 + self.value * 0.01)

@Effect.register("SHIELD")
class Shield(Ward):
    type = "SHIELD"

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
    
    def store_at(self):
        return "PLAYER"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 - self.value * 0.01)

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
        return f"{self.type}: {self.duration}"
    
    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        self.duration -= 1

# decreases health
class DOT(Effect):
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

    def store_at(self):
        return "PLAYER"

    def begin_round(self):
        pass

    def end_round(self):
        self.duration -= 1

# increases health
class HOT(Effect):
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

    def apply(self, match, caster, enemy, effect):
        match.play_gambit(caster, enemy, self)