import random
from .effects import Effect, Pip, Weakness

class Action:
    def __init__(self, effect, caster, enemy, match, context):
        self.effect = effect
        self.caster = caster
        self.enemy = enemy
        self.match = match
        self.context = context

    def do_damage(self):
        print("doing damage...")
        print(f"effect: {self.effect}")
        if self.effect.target == "SELF":
            abs_target = self.caster
        elif self.effect.target == "ENEMY":
            abs_target = self.enemy

        if self.effect.type == "SINGLE_DAMAGE":
            effect_value = self.effect.value
        elif self.effect.type == "RANGE_DAMAGE":
            effect_value = random.randrange(self.effect.min, self.effect.max, 5)
        elif self.effect.type == "PERCENT_DAMAGE":
            effect_value = self.effect.value*0.01*abs_target.max_health
            abs_target.dec_health(effect_value)
            print(f"Does {effect_value} damage!")
            print(f"{abs_target.name} HEALTH: {abs_target.curr_health}")
            return
        
        print(f"Base effect val: {effect_value}")

        effect_school = self.effect.school

        pierce_val = self.caster.pierce[effect_school]

        print(f"caster pierce: {pierce_val} {effect_school}") 

        effect_value = self.caster.mod_casting_damage(effect_value, effect_school, self.context)

        b = self.match.global_effect

        if b:
            if b.school == effect_school:
                effect_value += effect_value * b.value * 0.01

        effect_value = abs_target.mod_incoming_damage(effect_value, effect_school, pierce_val)

        abs_target.dec_health(effect_value)
        print(f"Does {effect_value} damage!")
        print(f"{abs_target.name} HEALTH: {abs_target.curr_health}")

    def play_if_gambit(self):
        met_cond = True

        for condition in self.effect.cause:
            if condition.get("TARGET") == "SELF":
                abs_target = self.caster
            else:
                abs_target = self.enemy

            match condition.get("ACTION"):
                case "GAMBIT":
                    if condition.get("TYPE") == "AURA":
                        if not abs_target.aura:
                            met_cond = False
                        else:
                            abs_target.aura = None
                    else:
                        to_remove = []
                        gambit_type = condition.get("TYPE")
                        
                        for effect in self.enemy.effects[::-1]:
                            print(f"effect.type: {effect.type}, gambit_type: {gambit_type}")
                            if effect.type == gambit_type:
                                to_remove.append(effect)
                                
                                if len(to_remove) == condition.get("AMOUNT"):
                                    break

                        amount = len(to_remove)

                        print(f"amount: {amount}; max: {condition.get("AMOUNT")}")

                        if amount != condition.get("AMOUNT"):
                            met_cond = False

                        if met_cond:
                            for effect in to_remove:
                                abs_target.del_effect(effect)
        

        if met_cond:
            for todo in self.effect.then:
                effect_class = Effect.registry[todo["TYPE"]]
                effect_obj = effect_class.from_json(todo)
                effect_obj.apply(self, self.caster, self.enemy, self.context)
        else:
            for todo in self.effect.else_clause:
                effect_class = Effect.registry[todo["TYPE"]]
                effect_obj = effect_class.from_json(todo)
                effect_obj.apply(self, self.caster, self.enemy, self.context)

    def play_gambit(self):
        gambit_cause = self.effect.cause[0]
        print(gambit_cause)
        gambit_effect = self.effect.per_effect

    #  print(json.dumps(gambit_cause, indent=4))
    #  print(json.dumps(gambit_effect, indent=4)) 

        effect_target = gambit_cause.get("TARGET")

        if effect_target == "SELF":
            abs_target = self.caster
        elif effect_target == "ENEMY":
            abs_target = self.enemy
                
        match gambit_cause.get("ACTION"):
            case "STEAL":
                effect_count = 0
                gambit_type = gambit_cause.get("TYPE")
                if gambit_type == "PIP":
                    reg_pip = next((pip for pip in self.enemy.pips if pip.school == "REG"), None)
                    if reg_pip:
                        self.enemy.remove_pip(reg_pip)
                    else:
                        to_rem = self.caster.pips[0]
                    #   print(f"To remove pip: {to_rem}")
                        self.enemy.remove_pip(to_rem)
                        self.enemy.pips.insert(0, Pip("REG"))
                    effect_count += 1

                    return

                gambit_effect = self.effect.per_effect

                per_effect_type = gambit_effect.get("TYPE")

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)
                
                for _ in range(effect_count):
                    if per_effect_type == "PIP":
                    #    print(f"Adding a pip???")
                        new_effect = effect_obj.clone()
                        reg_idx = self.caster.last_pip_index("REG")

                        if reg_idx is None:
                            self.caster.pips.insert(0, new_effect)
                        else:        
                            self.caster.pips.insert(reg_idx + 1, new_effect)

                        continue
            case "ECHO":
                effect_count = 0
                # gambit_type = gambit_cause.get("TYPE")
                for effect in abs_target.effects:
                    if effect.type == gambit_cause.get("TYPE"):
                        effect_count += 1
                        
                        if effect_count == gambit_cause.get("MAX"):
                            break

                print(f"amount: {effect_count}")

                gambit_effect = self.effect.per_effect

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)

            #    per_effect_type = gambit_effect.get("TYPE")

                gambit_effect_target = gambit_effect["TARGET"]

                if gambit_effect_target == "SELF":
                    abs_target = self.caster
                elif gambit_effect_target == "ENEMY":
                    abs_target = self.enemy
                
                for _ in range(effect_count):
                    new_effect = effect_obj.clone()

                    if gambit_effect.get("TYPE") == "PIP":
                        reg_idx = self.caster.last_pip_index("REG")

                        if reg_idx is None:
                            self.caster.pips.insert(0, new_effect)
                        else:        
                            self.caster.pips.insert(reg_idx + 1, new_effect)

                        continue

                    abs_target.add_effect(new_effect)

                    print(f"Adding effect {new_effect} to {abs_target.name}")

            case "SWAP":
                from_caster = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in self.caster.effects[:-1]:
                    if effect.type == gambit_type:
                        from_caster.append(effect)
                        
                        if len(from_caster) == gambit_cause.get("MAX"):
                            break

                amount = len(from_caster)

                from_enemy = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in self.enemy.effects:
                    if effect.type == gambit_type:
                        from_enemy.append(effect)
                        
                        if len(from_enemy) == gambit_cause.get("MAX"):
                            break

                for effect in from_caster:
                    self.caster.del_effect(effect)

                    self.enemy.add_effect(effect)

                for effect in from_enemy:
                    self.enemy.del_effect(effect)

                    self.caster.add_effect(effect)

            case "DETONATE":
                to_explode = []
                gambit_type = gambit_cause.get("TYPE")

                for effect in abs_target.effects:
                    if effect.type == gambit_type:
                        to_explode.append(effect)
                        
                        if len(to_explode) == gambit_cause.get("MAX"):
                            break

                amount = len(to_explode)

                for effect in to_explode:
                    multiplier = gambit_cause.get("VALUE")
                    abs_target.explode_dot(effect, multiplier)

            case "GAMBIT":
                to_remove = []
                gambit_type = gambit_cause.get("TYPE")

                cause_target = gambit_cause.get("TARGET")

                if cause_target == "SELF":
                    abs_target = self.caster
                elif cause_target == "ENEMY":
                    abs_target = self.enemy

                for effect in self.caster.effects[::-1]:
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)

                for effect in to_remove:
                    abs_target.del_effect(effect)


                per_effect_type = gambit_effect.get("TYPE")
                
                for _ in range(amount):
                    if per_effect_type == "HEAL_WEAKNESS":
                        gambit_effect_target = gambit_effect["TARGET"]

                        if gambit_effect_target == "SELF":
                            abs_target = self.caster
                        elif gambit_effect_target == "ENEMY":
                            abs_target = self.enemy

                        per_effect_value = gambit_effect.get("VALUE")
                        per_effect_family = gambit_effect.get("FAMILY")

                        hiii = Weakness(per_effect_value, per_effect_family)

                        self.add_effect(abs_target, hiii)

            case "CLEAR":
                to_remove = []
                gambit_type = gambit_cause.get("TYPE")
                for effect in abs_target.effects[::-1]:
                    print(f"CLEARING effect: {effect}")
                    if effect.type == gambit_type:
                        to_remove.append(effect)
                        
                        if len(to_remove) == gambit_cause.get("MAX"):
                            break

                amount = len(to_remove)

                print(f"amount: {amount}")

                for effect in to_remove:
                    abs_target.del_effect(effect)

                gambit_effect = self.effect.per_effect

                per_effect_type = gambit_effect.get("TYPE")

                effect_class = Effect.registry[gambit_effect["TYPE"]]
                effect_obj = effect_class.from_json(gambit_effect)

                if hasattr(effect_obj, "school"):
                    if effect_obj.school == "ENEMY_SCHOOL":
                        effect_obj.school = self.enemy.school
                    elif effect_obj.school == "ALLY_SCHOOL":
                        effect_obj.school = self.caster.school

                gambit_effect_target = gambit_effect["TARGET"]


                if gambit_effect_target == "SELF":
                    abs_target = self.caster
                elif gambit_effect_target == "ENEMY":
                    abs_target = self.enemy
                
                for _ in range(amount):
                    if per_effect_type == "PIP":
                    #    print(f"Adding a pip???")
                        new_effect = effect_obj.clone()
                        reg_idx = self.caster.last_pip_index("REG")

                        if reg_idx is None:
                            self.caster.pips.insert(0, new_effect)
                        else:        
                            self.caster.pips.insert(reg_idx + 1, new_effect)

                        continue
                    else:
                        new_effect = effect_obj.clone()

                        print(f"Adding effect: {new_effect}")

                        abs_target.add_effect(new_effect)