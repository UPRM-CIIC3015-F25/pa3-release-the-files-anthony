from enum import Enum

class Suit(Enum): # Enumeration for the four card suits
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"

class Rank(Enum): # Enumeration for the thirteen card ranks
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Enhancement(Enum):
    BASIC = "Basic Card"
    BONUS = "Bonus Card"
    MULT = "Mult Card"
    WILD = "Wild Card"
    GLASS = "Glass Card"
    STEEL = "Steel Card"
    STONE = "Stone Card"
    GOLD = "Gold Card"
    LUCKY = "Lucky Card"

class Card:
    def __init__(self, suit: Suit, rank: Rank, image=None, enhancement=Enhancement.BASIC): # Represents a single playing card with suit, rank, and optional image
        self.suit = suit
        self.rank = rank
        self.image = image
        self.faceDown = False
        self.isSelected = False
        self.enhancement = enhancement
        self.isDestroyed = False


        if rank.value <= 10: # Chip value based on rank
            self.chips = rank.value
        elif rank.value < 14:  # Face cards (Jack, Queen, King)
            self.chips = 10
        else:  # Ace
            self.chips = 11

    def get_pretty_enhancement_description(self) -> tuple[str, str]:
        enhancement_description = {
            "Basic Card": "Basic value for a card. So basic, in fact, that you shouldn't be seeing this text. What are you doing?",
            "Bonus Card": "Gives an additional +30 chips when scored",
            "Mult Card": "Gives an additional +4 Mult when scored",
            "Wild Card": "Card considered of every suit simultaneously",
            "Glass Card": "Gives *2 mult when scored [1 in 4 chance to self-destruct]",
            "Steel Card": "Gives *1.5 mult when held in hand",
            "Stone Card": "Always scores +50 chips, card not considered of any rank or suit",
            "Gold Card": "Gives $3 if held in hand AT THE END OF THE ROUND",
            "Lucky Card": "1 in 5 chance to give +20 mult when scored, 1 in 15 chance to give $20"
        }
        e_text = self.enhancement.value
        return e_text, enhancement_description.get(e_text, "[DESCRIPTIONNOTFOUND]")

    def update_enhancement(self, enhancement: Enhancement):
        self.enhancement = enhancement
        return self

    def __str__(self): # Formated string of the card (Example: Ace♠)
        return f"{self.rank.name.capitalize()}{self.suit.value}"