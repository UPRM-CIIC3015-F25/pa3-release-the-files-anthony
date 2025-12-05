from enum import Enum
from Cards.Card import Card, Rank, Suit, Enhancement
import random

HAND_VALUES = {
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "One Pair": 2,
    "High Card": 1,
    "": 0
    }

# DONE (TASK 3): Implement a function that evaluates a player's poker hand.
#   Loop through all cards in the given 'hand' list and collect their ranks and suits.
#   Use a dictionary to count how many times each rank appears to detect pairs, three of a kind, or four of a kind.
#   Sort these counts from largest to smallest. Use another dictionary to count how many times each suit appears to check
#   for a flush (5 or more cards of the same suit). Remove duplicate ranks and sort them to detect a
#   straight (5 cards in a row). Remember that the Ace (rank 14) can also count as 1 when checking for a straight.
#   If both a straight and a flush occur in the same suit, return "Straight Flush". Otherwise, use the rank counts
#   and flags to determine if the hand is: "Four of a Kind", "Full House", "Flush", "Straight", "Three of a Kind",
#   "Two Pair", "One Pair", or "High Card". Return a string with the correct hand type at the end.
def evaluate_hand(hand: list[Card]):
    current_hands = set()

    rank_counts: dict[Rank, int] = {}
    suit_counts: dict[Suit, int] = {}
    for card in hand:
        rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
        if card.enhancement == Enhancement.WILD:
            suit_counts[Suit.SPADES] = suit_counts.get(Suit.SPADES, 0) + 1
            suit_counts[Suit.HEARTS] = suit_counts.get(Suit.HEARTS, 0) + 1
            suit_counts[Suit.CLUBS] = suit_counts.get(Suit.CLUBS, 0) + 1
            suit_counts[Suit.DIAMONDS] = suit_counts.get(Suit.DIAMONDS, 0) + 1



    # Check for hand types
    for rank in rank_counts:
        match rank_counts[rank]:
            case 2:
                if "One Pair" in current_hands:
                    current_hands.add("Two Pair")
                elif "Three of a Kind" in current_hands:
                    current_hands.add("Full House")

                current_hands.add("One Pair")
            case 3:
                if "One Pair" in current_hands:
                    current_hands.add("Full House")

                current_hands.add("Three of a Kind")
            case 4:
                current_hands.add("Four of a Kind")
            case 5:
                pass

    # Check for flushes
    for suit in suit_counts:
        if suit_counts[suit] >= 5:
            current_hands.add("Flush")

    # Check for Flush House
    if ("Flush" in current_hands) and ("Full House" in current_hands):
        current_hands.add("Flush House")

    # Check for straights and royal
    royal_list = {Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN}
    ranks_set = set()
    for card in hand:
        ranks_set.add(card.rank)

    has_straight = False
    has_royal = False
    if len(hand) >= 5:
        ranks_list = list(ranks_set)
        ranks_list.sort(key=lambda r: r.value)
        has_straight = True
        has_royal = True
        for i in range(len(ranks_list) - 1):
            card_rank = ranks_list[i]
            next_card_rank = ranks_list[i + 1]
            if card_rank.value != next_card_rank.value - 1:
                # NOTE: Straight only works for numerical sequences or for
                # [A, 5, 4, 3, 2], like in base Balatro.
                # It does not numerically shift or overflow the other values
                if not ((card_rank.value == 5) and (Rank.ACE in ranks_list)):
                    has_straight = False
                    break

            if card_rank not in royal_list:
                has_royal = False

    if has_straight:
        current_hands.add("Straight")
        if has_royal and ("Flush" in current_hands):
            current_hands.add("Royal Flush")


    # Final Selection: Check the highest value possible with the hand
    max_hand: str = ""
    max_hand_value: int = HAND_VALUES[max_hand]
    for play_hand in current_hands:
        score_hand = "Straight Flush" if (play_hand == "Royal Flush") else play_hand
        score_hand = "Flush House" if (play_hand == "Flush House") else play_hand
        if HAND_VALUES[score_hand] > max_hand_value:
            max_hand_value = HAND_VALUES[score_hand]
            max_hand = play_hand

    # Return the final selection if something of the above
    if max_hand != "":
        return max_hand

    return "High Card"

def Enhancments_fun(hand: list[Card]):
    destroyed = []
    hand_type = evaluate_hand(hand)
    total_chips = sum(c.chips for c in hand if c.enhancement != Enhancement.STONE)
    mult = 1.0
    cash = 0.0

    for card in hand:
        enh = card.enhancement

        if enh == Enhancement.BONUS:
            total_chips += 30

        elif enh == Enhancement.MULT:
            mult += 4

        elif enh == Enhancement.GLASS:
            mult *= 2
            if random.random() < 0.25:
                card.isDestroyed = True
                destroyed.append(card)

        elif enh == Enhancement.STEEL:
            mult *= 1.5

        elif enh == Enhancement.STONE:
            total_chips += 50

        elif enh == Enhancement.LUCKY:
            if random.random() < 0.20:
                mult += 20
            if random.random() < 1 / 15:
                cash += 20.0

        elif enh == Enhancement.GOLD:
            cash += 3.0

    total_score = total_chips * mult

    return {
        "hand_type": hand_type,
        "chips": total_chips,
        "multiplier": mult,
        "total_score": total_score,
        "cash": cash,
        "destroyed": destroyed
    }