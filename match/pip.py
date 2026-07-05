class Pip():
    type = "PIP"
    def __init__(self, school):
        self.school = school

    def __str__(self):
        return f"{self.type}: {self.school}"
    
    def __repr__(self):
        return str(self)