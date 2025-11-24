class TarotCard:
    def __init__(self, name, description, price=6, image=None, isConsumed=False):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.isConsumed = isConsumed

    def __str__(self):
        return f"{self.name}: {self.description}"

    def sellPrice(self):
        return int(self.price * 0.6)

Tarots = {
    "Silver Chariot": TarotCard("Silver Chariot", "levels up High Card", 6),
    "Magician's Red": TarotCard("Magician's Red", "levels up One Pair", 6),
    "Star Platinum": TarotCard("Star Platinum", "levels up Two Pair", 6),
    "Hierophant Green": TarotCard("Hierophant Green", "levels up Three of a Kind", 6),
    "Justice": TarotCard("Justice", "levels up Straight", 6),
    "Judgment": TarotCard("Judgment", "Creates a random Joker card", 6),
    "The Fool": TarotCard("The Fool", "levels up Full House", 6),
    "The Emperor": TarotCard("The Emperor", "levels up Four of a Kind", 6),
    "The Hanged Man": TarotCard("The Hanged Man", "levels up all hands", 6),
    "Death 13": TarotCard("Death 13", "levels up all hands", 6),
    "The World": TarotCard("The World", "levels up all hands", 6)
}