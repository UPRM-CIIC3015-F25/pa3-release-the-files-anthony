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
