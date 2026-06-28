# class Effect:
#     def __init__(
#             self,
#             effect_type,
#             effect_obj
#     ):
#         self.effect_type = effect_type
#         self.effect_obj = effect_obj

#     def get_effect_obj(self):
#         return self.effect_obj

class Effect():
    def __str__(self):
        return self.type

    type = None

    def begin_round(self):
        pass

    def end_round(self):
        pass

    def expired(self):
        return False

class Bubble(Effect):
    def __init__(
            self,
            school,
            value
    ):
        self.type = "BUBBLE"
        self.school = school
        self.value = value

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

class Damage:
    def __init__(
            self,
            school,
            value
    ):
        self.school = school
        self.value = value

class Heal:
    def __init__(
            self,
            value
    ):
        self.value = value

class Charm(Effect):
    def __init__(
            self,
            polarity,
            school,
            value
    ):
        self.type = "CHARM"
        self.polarity = polarity
        self.school = school
        self.value = value

    def begin_round(self):
        pass
    
    def end_round(self):
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
    
class Trap(Ward):
    def __init__(
            self,
            school,
            value,
            family
    ):
        super().__init__(school, value, family)
        self.type = "TRAP"

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
    def begin_round(self):
        pass

    def end_round(self):
        pass

    def mod_damage(self, damage):
        return damage * (1 + self.value * 0.01)

class Shield(Ward):
    def __init__(
            self,
            school,
            value,
            family
    ):
        super().__init__(school, value, family)
        self.type = "SHIELD"

    def __str__(self):
        return f"{self.type}: {self.school} {self.value}"
    
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
class Aura(Effect):
    def __init__(
            self,
            duration,
            adj
            # the effects are just charms/wards
    ):
        self.type = "AURA"
        self.duration = duration
        self.adj = adj

    def __str__(self):
        return f"{self.type}: {self.duration}"

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

    def begin_round(self):
        pass

    def end_round(self):
        self.duration -= 1

# #"TYPE": "BACKLASH",
#                 "DURATION": 3,
#                 "VALUE_TYPE": "PERCENT_MAX_HEALTH",
#                 "VALUE_PER_TURN": 5,
#                 "CONDITION": {
#                     "EFFECT": "POSITIVE_CHARM",
#                     "TARGET": "SELF"
#                 }
class Backlash(Effect):
    def __init__(
            self,
            duration,
            value_per_turn,
            condition
    ):
        self.type = "BACKLASH"
        self.school = "SHADOW"
        self.duration = duration
        self.value_per_turn = value_per_turn
        self.condition = condition

        self.curr_turn = 0
        self.accumulated = value_per_turn

    def __str__(self):
        return f"{self.type}: {self.accumulated} {self.duration}"

    def begin_round(self):
        pass

    def end_round(self):
        self.curr_turn += 1
        self.duration -= 1
    
    def inc_backlash(self):
        self.accumulated += self.value_per_turn

    def expired(self):
        return self.duration <= 1