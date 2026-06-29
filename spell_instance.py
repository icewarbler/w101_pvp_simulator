# This holds an instance of the current spell
# Used right now to hold blades for multiple damage effects in a single spell
# (wards do not need to be held)
class SpellInstance:
    def __init__(self, spell, caster, enemy):
        self.spell = spell
        
        self.caster = caster
        self.enemy = enemy

        self.charms_used = {}

    def add_used_charm(self, player, charm):
        self.charms_used[charm] = player