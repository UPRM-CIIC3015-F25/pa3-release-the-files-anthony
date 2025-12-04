from Cards.Card import Card, Suit
from Deck.HandEvaluator import Enhancments_fun, Enhancement



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
    def activateTarot(self, mutCardsSelected: list[Card] | None = None, player_hand: list[Card] | None = None):
        if mutCardsSelected is None:
            mutCardsSelected = []

        print(f"Tarot: {self.name}")
        print(f"Selected cards: {len(mutCardsSelected)}")
        print(f"Player hand: {len(player_hand) if player_hand else 0}")

        destroyed_cards = []
        enhanced_cards = []

        print("Before Tarot:", [(c.rank.name, c.suit.value, c.enhancement.name) for c in mutCardsSelected])
        match self.name:
            case "Silver Chariot":
                if mutCardsSelected:
                    c = mutCardsSelected[0]
                    enhanced_cards.append((Enhancement.STEEL, c.update_enhancement(Enhancement.STEEL)))

            case "Magician's Red":
                if mutCardsSelected:
                    for c in mutCardsSelected[:2]:
                       enhanced_cards.append((Enhancement.LUCKY, c.update_enhancement(Enhancement.LUCKY)))

            case "Hierophant Green":
                if mutCardsSelected:
                    for c in mutCardsSelected[:2]:
                        enhanced_cards.append((Enhancement.BONUS, c.update_enhancement(Enhancement.BONUS)))

            case "Justice":
                if mutCardsSelected:
                    c = mutCardsSelected[0]
                    enhanced_cards.append((Enhancement.GLASS, c.update_enhancement(Enhancement.GLASS)))

            case "Star Platinum":
                if mutCardsSelected:
                    for c in mutCardsSelected[:3]:
                        c.suit = Suit.DIAMONDS

            case "The World":
                if mutCardsSelected:
                    for c in mutCardsSelected[:3]:
                        c.suit = Suit.SPADES

            case "The Hanged Man":
                if mutCardsSelected:
                    for c in mutCardsSelected[:2]:
                        destroyed_cards.append(c)
                        print(f"DEBUG: The Hanged Man destroying {c.rank.name} of {c.suit.value}")

            case "Death 13":
                if mutCardsSelected and len(mutCardsSelected) >= 2:
                    left, right = mutCardsSelected[:2]
                    left.suit = right.suit
                    left.rank = right.rank
                    left.enhancement = right.enhancement
                    left.chips = right.chips

            # SPECIAL TAROTS (no card mutation)
            case "Judgment":
                return {"effect": "create_joker"}

            case "The Emperor":
                return {"effect": "create_tarots", "count": 2}

            case "The Fool":
                return {"effect": "recreate_last_used"}

            case _:
                raise NotImplementedError(f"Tarot effect for {self.name} not implemented")

        print("After Tarot:", [(c.rank.name, c.suit.value, c.enhancement.name) for c in mutCardsSelected])
        self.isConsumed = True

        if destroyed_cards:
            return {"destroyed_cards": destroyed_cards}

        if enhanced_cards:
            return {"enhanced_cards": enhanced_cards}


        if player_hand:
            result = Enhancments_fun(player_hand)
            print("Hand evaluation result:", result)
            return result

        return None
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