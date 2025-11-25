from Cards.Card import Card

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

    # TODO (BONUS): Give the cards selected (parameter: mutCardsSelected) the corresponding tarot card
    #   effect. The tarot card is given by self.name, and isConsumed must be set to true.
    #   HINT: I put in the mut thing to say that they're mutable. All properties must be given back to
    #   the cards, except for the cases of Judgement, The Fool and The Emperor.
    #   HINT 2: Google match statements, they make things easier in this case imo
    def activateTarot(self, mutCardsSelected: list[Card]|None = None):
        return NotImplementedError("Tag, you're it!")

TAROTS = {
    "Silver Chariot": TarotCard("Silver Chariot", "Enhances 1 selected card into a Steel Card", 3),
    "Magician's Red": TarotCard("Magician's Red", "Enhances 2 selected cards into Lucky Cards", 3),
    "Star Platinum": TarotCard("Star Platinum", "Converts up to 3 selected cards to Diamonds", 3),
    "Hierophant Green": TarotCard("Hierophant Green", "Enhances 2 selected cards to Bonus Cards", 3),
    "Justice": TarotCard("Justice", "Enhances 1 selected card into a Glass Card", 3),
    "Judgment": TarotCard("Judgment", "Creates a random Joker card (Must have room)", 3),
    "The Fool": TarotCard("The Fool", "Creates the last Tarot or Planet card used during this run (The Fool excluded)", 3),
    "The Emperor": TarotCard("The Emperor", "Creates up to 2 random Tarot cards [Must have room]", 3),
    "The Hanged Man": TarotCard("The Hanged Man", "Destroys up to 2 selected cards", 3),
    "Death 13": TarotCard("Death 13", "Select 2 cards, convert the left card into the right card [Drag to rearrange]", 3),
    "The World": TarotCard("The World", "Converts up to 3 selected cards to Spades", 3)
}