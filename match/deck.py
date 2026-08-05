import random

class Deck:
    def __init__(self, deck):
        self.cards = []
        max_cards = 7
        hand = []

        print(deck)
        deck_spells = deck["SPELLS"]

        for spell, count in deck_spells.items():
            self.cards.extend([spell] * count)
        
        random.shuffle(self.cards)

    def __str__(self):
        return "\n".join(self.cards)
    
    def draw(self):
        if not self.cards:
            return None
        
        return self.cards.pop()
    
    def delete(self, card):
        if card is None:
            return
        
        self.cards.remove(card)

class Hand:
    max_cards = 7

    def __init__(self):
        self.cards = []

    def __str__(self):
        return "\n".join(self.cards)

    def add(self, card):
        if card is None:
            return
        
        if len(self.cards) >= self.max_cards:
            raise ValueError("Hand is full!")
        
        self.cards.append(card)
    
    def delete(self, card):
        if card is None:
            return
        
        self.cards.remove(card)