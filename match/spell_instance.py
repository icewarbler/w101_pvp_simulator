# This holds an instance of the current spell
# Used right now to hold charms for multiple damage effects in a single spell
# (wards do not need to be held)
class SpellInstance:
    def __init__(self, spell, caster, enemy, pips, schoolpips, shadpips, multi=False):
        self.spell = spell
        
        self.caster = caster
        self.enemy = enemy

        self.charms_used = {}
        self.pips = pips
        self.schoolpips = schoolpips
        self.shadpips = shadpips

        self.multi = multi

    def add_used_charm(self, player, charm):
        self.charms_used[charm] = player