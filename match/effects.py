import json
from .dataloader import load_json

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

@Effect.register("PERCENT_DAMAGE")
class Percent_Damage:
    type = "PERCENT_DAMAGE"

    categories = {"DAMAGE", "PERCENT_DAMAGE"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["TARGET"], effect["VALUE"])
    
    def __init__(
            self,
            target,
            value
    ):
        self.target = target
        self.value = value

    def __str__(self):
        return f"{self.type}: {self.value}"
    
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

@Effect.register("IF_GAMBIT")
class Gambit(Effect):
    type = "IF_GAMBIT"

    categories = {"GAMBIT", "IF_GAMBIT"}

    @classmethod
    def from_json(cls, effect):
        return cls(effect["CAUSE"], effect["THEN"], effect["ELSE"])
    
    def __init__(self, cause, then, else_clause):
        self.cause = cause
        self.then = then
        self.else_clause = else_clause

    def __str__(self):
        return f"{self.type}"
    
    def store_at(self):
        return None

    def apply(self, match, caster, enemy, context):
        match.play_if_gambit(caster, enemy, self, context)

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

        # puts every entry read from minion_spells.json into a dict
        spell_lookup = { spell["ID"]: spell for spell in spells }

        spell = spell_lookup[spell_id]
        
        return spell

    def select_spell(self):
        pass

    def gen_hand(self):
        if self.id == "WATERELEMENTAL":
            if self.duration == 6:
                self.hand.add("BALANCEBLADE_25")
                self.hand.add("WEAKNESS_25")
            if self.duration == 4:
                self.hand.delete("BALANCEBLADE_25")
                self.hand.delete("WEAKNESS_25")
                self.hand.add("DOUBLEWEAKNESS_25")
                self.hand.add("GREATERWEAKNESS_35")
                self.hand.add("DUOCHROMABLADE_30")
                self.hand.add("GREATERSWORD_40")
        if self.id == "HELPFULMANDER":
            pass
    
    def add_effect(self, effect):
        self.effects.append(effect)

    def get_outgoing_damage(self, school):
        return self.outgoing_damage.get(school)

    def get_incoming_resist(self, school):
        return self.incoming_resist.get(school)
    
    def dec_health(self, value):
        self.curr_health -= value

        # this function modifies the casting damage
    # it is called in dot_damage and do_damage
    def mod_casting_damage(self, damage_val, damage_school, context):
        # gets caster's outgoing damage
        print(self.get_outgoing_damage(damage_school))
    # print(f"value: {effect_value}")
        damage_val += (damage_val * self.get_outgoing_damage(damage_school) * 0.01)

        if self.aura is not None:
            adj = self.aura.adj

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (damage_school, "UNIVERSAL"):
                    # ignore if not blade/weakness type aura
                    if modifier["TYPE"] == "WEAKNESS":
                        damage_val -= damage_val * modifier["VALUE"] * 0.01
                    elif modifier["TYPE"] == "BLADE":
                        damage_val += damage_val * modifier["VALUE"] * 0.01

        caster_charms = [ effect for effect in self.effects if isinstance(effect, Charm) ]
        
        used_charm_families = set()

        for charm in caster_charms:
            if charm.type == "HEAL_WEAKNESS":
                continue
            if charm.school in (damage_school, "UNIVERSAL"):
                if charm.family in used_charm_families:
                    continue
                used_charm_families.add(charm.family)
                print(f"Charm used: {charm.school} of val {charm.value}")
                damage_val = charm.mod_damage(damage_val)
                if charm not in context.charms_used:
                    context.add_used_charm(self, charm)

        return damage_val

    # this function modifies the incoming damage
    # it is called in do_tick and do_damage
    def mod_incoming_damage(self, damage_val, damage_school, pierce_val, is_dot=False):
        print(f"pierce_val: {pierce_val}")
        if self.aura is not None:
            adj = self.aura.adj

            # ignore if not correct school
            for modifier in adj:
                if modifier["SCHOOL"] in (damage_school, "UNIVERSAL"):
                    print(json.dumps(modifier, indent=4))
                    # ignore if not shield/trap type aura
                    if modifier["TYPE"] == "SHIELD":
                        mod_val = modifier["VALUE"]
                        print(f"mod_val: {mod_val}; pierce_val: {pierce_val}")
                        mod_val -= pierce_val
                        if mod_val < 0:
                            pierce_val = -(mod_val)
                            print(f"pierce_val: {pierce_val}; mod_val: {mod_val}")
                            mod_val = 0
                        damage_val -= damage_val * mod_val * 0.01
                    elif modifier["TYPE"] == "TRAP":
                        damage_val += damage_val * modifier["VALUE"] * 0.01

        # gets enemy shields/traps
        enemy_wards = [ effect for effect in self.effects if isinstance(effect, Ward) ]

        used_families = set()


        for ward in enemy_wards:
            if ward.school in (damage_school, "UNIVERSAL"):
                if ward.family in used_families:
                    continue
                if ward.type == "DOT_TRAP" and not is_dot:
                    continue
                used_families.add(ward.family)
                print(f"{ward.type} used: {ward.school} of val {ward.value}")
                pierce_val, damage_val = ward.mod_damage(damage_val, pierce_val)
                print(f"post-ward effect_value: {damage_val}; pierce_val: {pierce_val}")
                #   context.add_used_ward(abs_target, ward)
                self.del_effect(ward)

        # gets enemy resist
        enemy_res = self.get_incoming_resist(damage_school)
        print(f"init enemy res: {enemy_res}")
        enemy_res -= pierce_val
        print(f"enemy res: {enemy_res}; pierce_val: {pierce_val}")
        enemy_res = 0 if enemy_res < 0 else enemy_res
        damage_val -= damage_val * enemy_res * 0.01

        return damage_val

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

class Hand:
    max_cards = 7

    def __init__(self):
        self.cards = []

    def __str__(self):
        return "\n".join(self.cards)

    def add(self, card):
        if card is None:
            return
        
        self.cards.append(card)
    
    def delete(self, card):
        if card is None:
            return
        
        self.cards.remove(card)