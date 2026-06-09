class Effect:
    def __init__(
            self,
            effect_type,
            effect_obj
    ):
        self.effect_type = effect_type
        self.effect_obj = effect_obj


    def get_effect_obj(self):
        return self.effect_obj

class Damage:
    def __init__(
            self,
            target,
            school,
            value
    ):
        self.target = target
        self.school = school
        self.value = value

class Heal:
    def __init__(
            self,
            target,
            value
    ):
        self.target = target
        self.value = value

class Charm:
    def __init__(
            self,
            polarity,
            school,
            target,
            value
    ):
        self.polarity = polarity
        self.school = school
        self.target = target
        self.value = value

class Ward:
    def __init__(
            self,
            polarity,
            school,
            target,
            value
    ):
        self.polarity = polarity
        self.school = school
        self.target = target
        self.value = value

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
class Aura:
    def __init__(
            self,
            target,
            duration,
            adj
            # the effects are just charms/wards
    ):
        self.target = target
        self.duration = duration
        self.adj = adj

# decreases health
class DOT:
    def __init__(
            self,
            target,
            school,
            duration,
            stacks,
            value
    ):
        self.target = target
        self.school = school
        self.duration = duration
        self.stacks = stacks
        self.value = value

# increases health
class HOT:
    def __init__(
            self,
            target,
            duration,
            stacks,
            value
    ):
        self.target = target
        self.duration = duration
        self.stacks = stacks
        self.value = value

# #"TYPE": "BACKLASH",
#                 "DURATION": 3,
#                 "VALUE_TYPE": "PERCENT_MAX_HEALTH",
#                 "VALUE_PER_TURN": 5,
#                 "CONDITION": {
#                     "EFFECT": "POSITIVE_CHARM",
#                     "TARGET": "SELF"
#                 }
class Backlash:
    def __init__(
            self,
            duration,
            value_per_turn,
            condition
    ):
        self.duration = duration
        self.value_per_turn = value_per_turn
        self.condition = condition

        self.curr_turn = 0
        self.accumulated = value_per_turn

    def add_turn(self):
        self.curr_turn += 1
        self.accumulated += self.value_per_turn