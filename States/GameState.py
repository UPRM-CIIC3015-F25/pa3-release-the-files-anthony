import pygame
import random
from States.Menus.DebugState import DebugState
from States.Core.StateClass import State
from Cards.Card import Suit, Rank, Enhancement
from Cards.Jokers import Jokers
from Cards.Planets import PLANETS, PlanetCard
from Cards.Tarots import TAROTS, TarotCard
from States.Core.PlayerInfo import PlayerInfo
from Deck.HandEvaluator import evaluate_hand
from Levels.SubLevel import Blind


HAND_SCORES = {
    "Straight Flush": {"chips": 100, "multiplier": 8, "level": 1},
    "Four of a Kind": {"chips": 60, "multiplier": 7, "level": 1},
    "Full House": {"chips": 40, "multiplier": 4, "level": 1},
    "Flush": {"chips": 35, "multiplier": 4, "level": 1},
    "Straight": {"chips": 30, "multiplier": 4, "level": 1},
    "Three of a Kind": {"chips": 30, "multiplier": 3, "level": 1},
    "Two Pair": {"chips": 20, "multiplier": 2, "level": 1},
    "One Pair": {"chips": 10, "multiplier": 2, "level": 1},
    "High Card": {"chips": 5, "multiplier": 1, "level": 1},
}





class GameState(State):
    def __init__(self, nextState: str = "", player: PlayerInfo = None):
        super().__init__(nextState)
        # ----------------------------Deck and Hand initialization----------------------------
        self.playerInfo = player # playerInfo object
        self.deck = State.deckManager.shuffleDeck(State.deckManager.createDeck(self.playerInfo.levelManager.curSubLevel))
        self.hand = State.deckManager.dealCards(self.deck, 8)
        self.cards = {}
        
        self.jokerDeck = State.deckManager.createJokerDeck()
        self.consumableDeck = State.deckManager.createConsumableDeck()
        State.deckManager.shuffleDeck(self.consumableDeck)
        self.playerJokers = []
        self.playerConsumables = []
        self.jokers = {}
        self.consumables = {}
        # track which jokers activated for the current played hand (used to offset their draw)
        self.activated_jokers = set()
        self.card_usage_history = []
        # Keep track of the enhanced cards
        self.enhanced_cards = []
        # Game over flag
        self.gameOverTriggered = False

        # Tarot card tests
        test_tarots = ["Judgment", "The Emperor", "The Hanged Man", "Hierophant Green"]
        for tarot_name in test_tarots:
            if tarot_name in TAROTS:
                self.consumableDeck.append(TAROTS[tarot_name])

        # Add to playerConsumables
        self.playerConsumables.extend(test_tarots)

        # Soul logic
        self.showReviveOption = False
        self.dialogBoxRect = pygame.Rect(400, 300, 500, 200)
        self.yesButtonRect = pygame.Rect(450, 400, 100, 50)
        self.noButtonRect = pygame.Rect(650, 400, 100, 50)

        print("DEBUG: Player consumables:", self.playerConsumables)
        print("DEBUG: Consumable deck has:", [c.name for c in self.consumableDeck])

        #cool sounds
        self.use_sound = pygame.mixer.Sound("Graphics/Sounds/rupee.wav")
        self.use_sound.set_volume(1.0)
        self.destroy_sound = pygame.mixer.Sound("Graphics/Sounds/thunder.wav")
        self.destroy_sound.set_volume(1.0)
        self.buy_sound = pygame.mixer.Sound("Graphics/Sounds/buySFX.wav")
        self.buy_sound.set_volume(1.0)

        # for joker in self.jokerDeck:
        #     print(joker.name)
        
        self.cardsSelectedList = []
        self.cardsSelectedRect = {}
        self.playedHandNameList = ['']
        self.used = []
        self.sorting = ""

        self.redTint = pygame.image.load("Graphics/Backgrounds/redTint.png").convert_alpha()
        self.redTint = pygame.transform.scale(self.redTint, (1300, 750))
        self.showRedTint = False
        self.redAlpha = 0

        self.gameOverSound = pygame.mixer.Sound("Graphics/Sounds/gameEnd.mp3")
        self.gameOverSound.set_volume(0.6)  # adjust loudness if needed

        # --------------------------------Images----------------------------------------------
        self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
        self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        self.smallBlind = pygame.image.load('Graphics/Backgrounds/Blinds/smallBlind.png')

        self.tvOverlay = pygame.image.load('Graphics/Backgrounds/CRT.png').convert_alpha()
        self.tvOverlay = pygame.transform.scale(self.tvOverlay, (1300, 750))
        # ----------------------------Player Options UI---------------------------------------

        # -----------------------Player Joker/Consumable Manip -------------------------------
        self.selected_info = None # Dictionary, information that you selected if you selected a joker or consumable

        self.joker_for_sell = None  # (joker_obj, screen_rect)
        self.joker_for_use = None  # (joker_obj, screen_rect)
        self.sell_rect = None  # screen-space sell button rect
        self.use_rect = None # screen space use button rect

        # ----------------------------Boss Theme & Background----------------------------
        # Use the music channel for background themes (main/boss) to avoid overlaps
        self.bossMusic_path = "Graphics/Sounds/bossBlindTheme.mp3"
        self.bossBackgroundImage = pygame.image.load('Graphics/Backgrounds/bossBG.png')
        self.bossBackground = pygame.transform.scale(self.bossBackgroundImage, (1300, 750))
        self.isBossActive = False
        self.bossMusicPlaying = False

        self.playerOpcions = pygame.Surface((500, 650), pygame.SRCALPHA)
        self.playerOpcionsRect = pygame.Rect(460, 650, 400, 100)

        total_w = self.playerOpcions.get_width()
        third_w = total_w // 3
        btn_h = 84

        self.playHandButtonRect = pygame.Rect(0, 0, third_w, btn_h)
        self.sortHandRect = pygame.Rect(third_w, 0, third_w, btn_h)
        self.discardButtonRect = pygame.Rect(third_w * 2, 0, third_w, btn_h)

        inner_margin = 8
        inner_w = (self.sortHandRect.width - inner_margin * 3) // 2
        inner_h = 48
        self.sort_inner_shift = 9
        inner_y = (self.sortHandRect.height - inner_h) // 2 + self.sort_inner_shift
        self.sortRankRect = pygame.Rect(self.sortHandRect.x + inner_margin, inner_y, inner_w, inner_h)
        self.sortSuitRect = pygame.Rect(self.sortHandRect.x + inner_margin * 2 + inner_w, inner_y, inner_w, inner_h)

        # -------------------------------Text surfaces--------------------------------------
        self.playHandText = self.playerInfo.textFont2.render("Play Hand", False, 'white')
        self.discardText = self.playerInfo.textFont2.render("Discard", False, 'white')
        self.sortRankText = self.playerInfo.textFont2.render("Rank", False, 'white')
        self.sortSuitText = self.playerInfo.textFont2.render("Suit", False, 'white')
        self.sortTitleText = self.playerInfo.textFont2.render("Sort Hand", False, 'white')

        # ----------------------------Game Areas----------------------------------------------
        self.centerCardsRect = pygame.Rect(450, 300, 500, 140)
        self.centerCardsSurface = pygame.Surface(self.centerCardsRect.size, pygame.SRCALPHA)
        self.deckContainer = pygame.Rect(380, 510, 680, 120)
        self.jokerContainer = pygame.Rect(380, 40, 340, 130)
        self.consumableContainer = pygame.Rect(980, 40, 220, 130)
        self.pileContainer = pygame.Rect(1120, 550, 100, 140)

        # ----------------------------Sound Effects-------------------------------------------
        self.select_sfx = pygame.mixer.Sound('Graphics/Sounds/selectCard.ogg')
        self.deselect_sfx = pygame.mixer.Sound('Graphics/Sounds/deselectCard.ogg')

        # ----------------------------Deck Pile UI--------------------------------------------
        self.show_deck_pile = False
        self.deck_button_rect = self.pileContainer.copy()

        # ----------------------------Play Hand Logic-----------------------------------------
        self.playHandActive = False
        self.playHandStartTime = 0
        self.playHandDuration = 5000   # show chips/mult for 5 seconds
        self.playedHandName = ""
        self.playedHandTextSurface = None
        self.scoreBreakdownTextSurface = None
        self.pending_round_add = 0      # amount to add to roundScore when timer expires

        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

        # ------ Debug Overlay Setup -------
        self.debugState = DebugState(game_state=self)
        # ------------------------------------------------------------------------------------

    def _pretty_joker_description(self, joker_obj):
        desc_map = {
            "The Joker": "Increase the hand multiplier by +4.",
            "Michael Myers": "Add a random multiplier between 0 and 23.",
            "Fibonacci": "For each Ace/2/3/5/8 played, add +8 to the multiplier.",
            "Gauntlet": "Grant +250 chips but reduce remaining hands by 2.",

            "Ogre": "Add +3 to the multiplier for each joker you own.",
            "Straw Hat": "Grant +100 chips, then -5 per hand already played this round.",
            "Hog Rider": "If the played hand is a Straight, add +100 chips.",
            "? Block": "If the played hand used exactly 4 Cards, add +4 chips.",
            "Hogwarts": "Each Ace played grants +4 multiplier and +20 chips.",
            "802": "If this is the last hand of the round, double the final gain.",
        }
        return desc_map.get(joker_obj.name, "No description available.")

    def gray_overlay_(self, destSurface, rect):
        shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 180))
        destSurface.blit(shade, rect.topleft)

    def update(self):
        # Always update LevelManager first so win/levelFinished flags are fresh
        self.playerInfo.levelManager.update()

        # If LevelManager flagged playerWins (no more levels), transition to GameWinState
        if self.playerInfo.levelManager.playerWins:
            self.isFinished = True
            self.nextState = "GameWinState"
            self.switchToNormalTheme()
            # dont continue updating GameState
            return

        if self.showReviveOption:
            # Only update the debug state, nothing else
            self.debugState.update()
            return
        # Check if we need to reset deck (coming back from LevelSelectState)
        if self.deckManager.resetDeck:
            self.deck = State.deckManager.shuffleDeck(State.deckManager.createDeck(self.playerInfo.levelManager.next_unfinished_sublevel()))
            self.hand = State.deckManager.dealCards(self.deck, 8, self.playerInfo.levelManager.next_unfinished_sublevel())
            self.used = []
            self.cardsSelectedList = []
            self.cardsSelectedRect = {}
            self.updateCards(400, 520, self.cards, self.hand, scale=1.2)
            self.deckManager.resetDeck = False  # Clear the flag

        # Check if level is finished and transition to LevelSelectState
        if self.playerInfo.levelFinished:
            reward = self.calculate_gold_reward(self.playerInfo)
            self.playerInfo.playerMoney += reward
            self.playerInfo.amountOfHands = 4
            self.playerInfo.amountOfDiscards = 4
            self.playerInfo.update()
            self.drawDeckPile()
            self.drawJokers()
            self.drawConsumables()
            self.drawDeckContainer()
            self.screen.blit(self.tvOverlay,(0,0))

            self.playerInfo.hasRevivedThisBlind = False

            State.screenshot = self.screen.copy()
            State.player_info = self.playerInfo
            self.isFinished = True
            self.deck = State.deckManager.shuffleDeck(State.deckManager.createDeck(self.playerInfo.levelManager.next_unfinished_sublevel()))
            self.hand = State.deckManager.dealCards(self.deck, 8, self.playerInfo.levelManager.next_unfinished_sublevel())
            self.playerInfo.amountOfHands = 4
            self.nextState = "ShopState"




            return

        # Heat stuff
        if self.playerInfo.isHeatActive:
            # Reduce heat duration
            self.playerInfo.heatDuration -= 1  # Assuming this runs ~60 times per second

            # Check if heat duration expired
            if self.playerInfo.heatDuration <= 0:
                # Level down or deactivate heat
                if self.playerInfo.heat_level > 1:
                    self.playerInfo.heat_level -= 1
                    print(f"HEAT LEVEL DOWN: Now at level {self.playerInfo.heat_level}")

                    # Set new duration based on current level
                    if self.playerInfo.heat_level == 2:
                        self.playerInfo.heatDuration = 300  # 5 seconds at 60 FPS
                    elif self.playerInfo.heat_level == 1:
                        self.playerInfo.heatDuration = 300  # 5 seconds at 60 FPS
                else:
                    # Heat completely depleted
                    self.playerInfo.heat_level = 0
                    self.playerInfo.isHeatActive = False
                    print("HEAT DEPLETED: Heat mode ended!")


        # Handle boss level music switching
        bossName = self.playerInfo.levelManager.curSubLevel.bossLevel
        if bossName and not self.isBossActive:
            self.isBossActive = True
            self.switchToBossTheme()
        elif not bossName and self.isBossActive:
            self.isBossActive = False
            self.switchToNormalTheme()
            
        # Handle play hand timing
        if self.playHandActive and self.playHandStartTime > 0:
            curTime = pygame.time.get_ticks()
            if curTime - self.playHandStartTime > self.playHandDuration:
                # Commit pending round addition and reset displayed chips/multiplier
                if getattr(self, "pending_round_add", 0) > 0:
                    old_score = self.playerInfo.roundScore
                    self.playerInfo.roundScore += self.pending_round_add
                    new_score = self.playerInfo.roundScore

                    target_score = self.playerInfo.levelManager.curSubLevel.score
                    if new_score > target_score and old_score <= target_score:
                        print(f"DEBUG: Officially beat blind! {old_score} -> {new_score} > {target_score}")

                        # Check if it's a boss blind
                        current_blind = self.playerInfo.levelManager.curSubLevel.blind
                        is_boss_blind = current_blind == Blind.BOSS

                        if is_boss_blind:
                            print("bigu bossu - OFFICIALLY BEAT BOSS BLIND!")
                            boss_souls = 5
                            # More heat if you beat boss blind
                            heat_gain = 50
                            self.playerInfo.souls += boss_souls
                            print(f"BOSS DEFEATED! Earned {boss_souls} souls! Total: {self.playerInfo.souls}")
                        else:
                            heat_gain = 25

                        # Apply heat gain and check for level up
                        self.playerInfo.heat = min(self.playerInfo.heat + heat_gain, self.playerInfo.max_heat)
                        print(f"Heat gained! Current: {self.playerInfo.heat}/100 (Level {self.playerInfo.heat_level})")

                        # Check if heat level should increase
                        self.check_heat_level_up()
                    self.pending_round_add = 0

                self.playerInfo.playerChips = 0
                self.playerInfo.playerMultiplier = 0

                self.playerInfo.curHandOfPlayer = ""
                self.playerInfo.curHandText = self.playerInfo.textFont1.render("", False, 'white')

                self.playHandActive = False
                # clear activated jokers when the display period ends so they return to normal position
                self.activated_jokers.clear()
                self.playHandStartTime = 0
                # Special boss effect: The Hook discards 2 random Cards from the hand
                if bossName == "The Hook":
                    # choose Cards that are currently in hand and not the selected Cards
                    posiblesCardToDiscard = []
                    for card in self.hand:
                        if card not in self.cardsSelectedList:
                            posiblesCardToDiscard.append(card)

                    discardCount = min(2, len(posiblesCardToDiscard)) # what happends if less than 2 Cards available?
                    if discardCount > 0:
                        cardsToDiscard = random.sample(posiblesCardToDiscard, discardCount)
                        for c in cardsToDiscard:
                                self.used.append(c)
                                self.hand.remove(c)
                                self.deselect_sfx.play()


                self.discardCards(removeFromHand=True)
        self.draw()
        self.checkHoverCards()
        self.debugState.update()

    def draw(self):
        # mess with this later (Change the bg to black)
        if self.showReviveOption:
            self.screen.fill((0, 0, 0))
            tint = pygame.Surface((1300, 750), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 180))
            self.screen.blit(tint, (0, 0))
            self.drawGameOverScreen()
            return
        # --- Call funcions ---
        self.playerInfo.update()
        self.drawDeckContainer()
        self.drawCardsInHand()
        self.drawCenterCards()
        self.drawJokers()
        self.drawConsumables()
        self.drawJokerTooltip()
        self.drawDeckPile()
        self.drawPlayerOptions()
        self.drawPlayedHandName()
        self.drawDeckPileOverlay()
        self.drawUse()
        self.drawSell()
        self.drawHeatDisplay()

        # DRAW SOUL DISPLAY
        self.drawSoulDisplay()
        if self.showRedTint and not self.showReviveOption:
            tint = pygame.Surface((1300, 750), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 180))
            self.screen.blit(tint, (0, 0))

        self.screen.blit(self.tvOverlay, (0, 0))

    def switchToBossTheme(self):
        # Switch background music to the boss theme using the music channel
        if not self.bossMusicPlaying:
            pygame.mixer.music.load(self.bossMusic_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
            self.bossMusicPlaying = True

    def switchToNormalTheme(self, force=False):
        # Restore the normal main theme on the music channel
        if self.bossMusicPlaying or force:
            pygame.mixer.music.load("Graphics/Sounds/mainTheme.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            self.bossMusicPlaying = False

    # ----------------------------Draw Methods------------------------------------------------
    def drawDeckContainer(self):
        deckContainer = pygame.Surface(self.deckContainer.size, pygame.SRCALPHA)
        pygame.draw.rect(deckContainer, (0, 0, 0, 120), deckContainer.get_rect())
        self.screen.blit(deckContainer, self.deckContainer.topleft)

    def drawCardsInHand(self):
        for card in self.cards:
            if self.playHandActive and card in self.cardsSelectedList:
                continue
            img_to_draw = getattr(card, "scaled_image", card.image)
            State.screen.blit(img_to_draw, self.cards[card])
        self.drawCardTooltip()

    def drawCenterCards(self):
        self.centerCardsSurface.fill((0, 0, 0, 0))  # Clear surface

        if len(self.cardsSelectedRect) > 0:
            for card, rect in self.cardsSelectedRect.items():
                img_to_draw = getattr(card, "scaled_image", card.image)
                self.centerCardsSurface.blit(img_to_draw, rect)

        self.screen.blit(self.centerCardsSurface, self.centerCardsRect)

    def drawPlayedHandName(self):
        if self.playHandActive and self.playedHandTextSurface:
            text_rect = self.playedHandTextSurface.get_rect(centerx=self.centerCardsRect.centerx)
            text_rect.bottom = self.centerCardsRect.top - 40  # Positioned higher
            self.screen.blit(self.playedHandTextSurface, text_rect)

        if self.playHandActive and self.scoreBreakdownTextSurface:
            score_rect = self.scoreBreakdownTextSurface.get_rect(centerx=self.centerCardsRect.centerx)
            # Position it relative to the hand name's rect for perfect alignment
            score_rect.top = text_rect.bottom + 5
            self.screen.blit(self.scoreBreakdownTextSurface, score_rect)

    def drawJokers(self):
        # Draw container background
        if self.showReviveOption:
            return
        jokerSurface = pygame.Surface(self.jokerContainer.size, pygame.SRCALPHA)
        pygame.draw.rect(jokerSurface, (0, 0, 0, 120), jokerSurface.get_rect(), border_radius=6)
        self.screen.blit(jokerSurface, self.jokerContainer.topleft)

        # Build joker objects list in the exact order of self.playerJokers
        player_joker_objs = []
        for name in self.playerJokers:
            for joker in self.jokerDeck:
                if joker.name == name:
                    player_joker_objs.append(joker)
                    break
        self.jokers.clear()
        n = max(1, len(player_joker_objs))
        inner_margin = 8
        avail_w = self.jokerContainer.width - inner_margin * (n + 1)
        slot_w = max(10, avail_w // n) if n > 0 else self.jokerContainer.width - inner_margin * 2
        slot_h = self.jokerContainer.height - inner_margin * 2

        for i, joker in enumerate(player_joker_objs):
            img = getattr(joker, "image", None)
            if img is None:
                continue

            # Determine scale to fit slot height
            target_h = slot_h
            iw, ih = img.get_width(), img.get_height()
            scale = 1.0
            if ih > 0 and ih != target_h:
                scale = target_h / ih
            new_w = max(1, int(iw * scale))
            new_h = max(1, int(ih * scale))
            scaled = pygame.transform.scale(img, (new_w, new_h))
            joker.scaled_image = scaled

            # center the scaled image inside its slot
            slot_x = self.jokerContainer.x + inner_margin + i * (slot_w + inner_margin)
            slot_y = self.jokerContainer.y + inner_margin
            # horizontally center within slot area
            draw_x = slot_x + max(0, (slot_w - new_w) // 2)
            draw_y = slot_y + max(0, (slot_h - new_h) // 2)

            rect = pygame.Rect(draw_x, draw_y, new_w, new_h)
            if self.playHandActive and joker.name in self.activated_jokers:
                rect = rect.move(0, 50)

            self.jokers[joker] = rect
            State.screen.blit(scaled, rect)

        # count/title text (keeps old placement just under container)
        jokerTitleText = self.playerInfo.textFont1.render((str(len(self.playerJokers))) + "/ 2", True, 'white')
        self.screen.blit(jokerTitleText, (self.jokerContainer.x + 1, self.jokerContainer.y + self.jokerContainer.height + 0))

    # DONE: Draw the consumable slot with really similar logic to drawJokers
    def drawConsumables(self):
        # Draw container background
        if self.showReviveOption:
            return
        consumableSurface = pygame.Surface(self.consumableContainer.size, pygame.SRCALPHA)
        pygame.draw.rect(consumableSurface, (0, 0, 0, 120), consumableSurface.get_rect(), border_radius=6)
        self.screen.blit(consumableSurface, self.consumableContainer.topleft)

        # Build consumable objects list in the exact order of self.playerConsumables
        player_consumable_objs = []
        for name in self.playerConsumables:
            for consum in self.consumableDeck:
                if consum.name == name:
                    player_consumable_objs.append(consum)
                    break


        self.consumables.clear()
        n = max(1, len(player_consumable_objs))
        inner_margin = 8
        avail_w = self.consumableContainer.width - inner_margin * (n + 1)
        slot_w = max(10, avail_w // n) if n > 0 else self.consumableContainer.width - inner_margin * 2
        slot_h = self.consumableContainer.height - inner_margin * 2

        for i, consum in enumerate(player_consumable_objs):
            img = getattr(consum, "image", None)
            if img is None:
                continue

            # Determine scale to fit slot height
            target_h = slot_h
            iw, ih = img.get_width(), img.get_height()
            scale = 1.0
            if ih > 0 and ih != target_h:
                scale = target_h / ih
            new_w = max(1, int(iw * scale))
            new_h = max(1, int(ih * scale))
            scaled = pygame.transform.scale(img, (new_w, new_h))
            consum.scaled_image = scaled

            # center the scaled image inside its slot
            slot_x = self.consumableContainer.x + inner_margin + i * (slot_w + inner_margin)
            slot_y = self.consumableContainer.y + inner_margin
            # horizontally center within slot area
            draw_x = slot_x + max(0, (slot_w - new_w) // 2)
            draw_y = slot_y + max(0, (slot_h - new_h) // 2)

            rect = pygame.Rect(draw_x, draw_y, new_w, new_h)
            if self.playHandActive:
                rect = rect.move(5, -10)

            self.consumables[consum] = rect
            State.screen.blit(scaled, rect)

        # count/title text (keeps old placement just under container)
        consumableTitleText = self.playerInfo.textFont1.render((str(len(self.playerConsumables))) + "/ 2", True, 'white')
        self.screen.blit(consumableTitleText, (self.consumableContainer.x + 1, self.consumableContainer.y + self.consumableContainer.height + 0))

    def drawHeatDisplay(self):
        heat = self.playerInfo.heat
        heat_level = self.playerInfo.heat_level
        is_active = self.playerInfo.isHeatActive

        # Heat bar background
        bar_width = 200
        bar_height = 20
        bar_x = 750
        bar_y = 50
        color = (0,0,0)

        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        if is_active:
            max_duration = 600 if heat_level == 3 else 300
            fill_ratio = self.playerInfo.heatDuration / max_duration
            fill_width = int(fill_ratio * bar_width)

            if heat_level == 1:
                color = (255, 100, 100)
            elif heat_level == 2:
                color = (255, 50, 50)
            elif heat_level == 3:
                color = (255, 0, 0)
            else:
                color = (100, 100, 100)

            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

            seconds_remaining = max(0, self.playerInfo.heatDuration) // 60
            time_text = self.playerInfo.textFont1.render(f"{seconds_remaining}s", True, (255, 255, 255))
            self.screen.blit(time_text, (bar_x + bar_width + 10, bar_y))
        else:
            fill_width = int((heat / 100) * bar_width)

            if heat_level == 0:
                color = (100, 100, 100)
            elif heat_level == 1:
                color = (150, 50, 50)
            elif heat_level == 2:
                color = (200, 50, 50)
            elif heat_level == 3:
                color = (255, 50, 50)

            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

            # Show heat percentage
            percent_text = self.playerInfo.textFont1.render(f"{heat}%", True, (255, 255, 255))
            self.screen.blit(percent_text, (bar_x + bar_width + 10, bar_y))

        # Heat level text
        level_text = self.playerInfo.textFont1.render(f"HEAT: {heat_level}", True, (255, 255, 255))
        self.screen.blit(level_text, (bar_x, bar_y - 25))

        # Active heat indicator
        if is_active:
            active_text = self.playerInfo.textFont1.render("HEAT ACTIVE!", True, (255, 255, 0))
            self.screen.blit(active_text, (bar_x, bar_y + 25))

    # --- Sell button (has duplicate in ShopState) -----
    def drawSell(self):
        if not self.joker_for_sell:
            self.sell_rect = None
            return

        joker_obj, joker_rect = self.joker_for_sell
        text = f"Sell : {joker_obj.sellPrice()}$"
        txt_surf = self.playerInfo.textFont2.render(text, True, (255, 255, 255))
        pad_x, pad_y = 10, 6
        box_w = txt_surf.get_width() + pad_x * 2
        box_h = txt_surf.get_height() + pad_y * 2
        box_x = joker_rect.centerx - box_w // 2
        box_y = joker_rect.bottom + 6
        self.sell_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (30, 200, 30), self.sell_rect, border_radius=6)
        self.screen.blit(txt_surf, (box_x + pad_x, box_y + pad_y))

    # ---- Use button (has duplicate in ShopState) -----
    def drawUse(self):
        if not self.joker_for_use:
            self.use_rect = None
            return

        joker_obj, joker_rect = self.joker_for_use
        text = f"Use"
        txt_surf = self.playerInfo.textFont2.render(text, True, (255, 255, 255))
        pad_x, pad_y = 10, 6
        box_w = txt_surf.get_width() + pad_x * 2
        box_h = txt_surf.get_height() + pad_y * 3
        box_x = joker_rect.centerx + 40
        box_y = (joker_rect.bottom + 6) // 2
        self.use_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (200, 0, 0), self.use_rect, border_radius=6)
        self.screen.blit(txt_surf, (box_x + pad_x, box_y + pad_y))

    def drawSoulDisplay(self):
        souls = getattr(self.playerInfo, 'souls', 0)

        try:
            soul_icon = pygame.image.load("Graphics/backgrounds/soul_icon.png").convert_alpha()
            soul_icon = pygame.transform.scale(soul_icon, (60, 60))
        except:
            # Fallback to drawn icon if image not found
            soul_icon = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(soul_icon, (200, 100, 255), (30, 30), 25)
            pygame.draw.circle(soul_icon, (255, 255, 255), (30, 30), 15)

        # Soul text
        souls_label = self.playerInfo.textFont1.render("Souls:", True, (200, 200, 200))  # Gray label
        souls_value = self.playerInfo.textFont1.render(f"{souls}", True, (255, 255, 255))  # White value

        # Position in top-right corner
        icon_x = 200  # Center position
        icon_y = 300  # Under round score

        # Calculate positions for label, value, and icon
        label_x = icon_x - souls_value.get_width() - souls_label.get_width() - 10
        label_y = icon_y + (75 - souls_label.get_height()) // 2

        value_x = icon_x - souls_value.get_width() - 5
        value_y = icon_y + (75 - souls_value.get_height()) // 2

        icon_x = icon_x
        icon_y = icon_y

        # Draw label, value, and icon
        self.screen.blit(souls_label, (label_x, label_y))
        self.screen.blit(souls_value, (value_x, value_y))
        self.screen.blit(soul_icon, (icon_x, icon_y))

    def drawDeckPile(self):
        pileContainer = pygame.Surface(self.pileContainer.size, pygame.SRCALPHA)
        pygame.draw.rect(pileContainer, (0, 0, 0, 120), pileContainer.get_rect())
        balatro_card = pygame.image.load('Graphics/Cards/Poker_Sprites.png').convert_alpha()
        card_width, card_height = 70, 94
        card_img = balatro_card.subsurface(pygame.Rect(0, 0, card_width, card_height))
        scaled_card = pygame.transform.scale(card_img, self.pileContainer.size)
        pileContainer.blit(scaled_card, (0, 0))
        self.screen.blit(pileContainer, self.pileContainer.topleft)
        pileCountText = self.playerInfo.textFont1.render(str(len(self.deck)) + "/44", True, 'white')
        textX = self.pileContainer.x + 5
        textY = self.pileContainer.y + self.pileContainer.height + 5
        self.screen.blit(pileCountText, (textX, textY))
        pygame.draw.rect(self.screen, (50, 50, 200), self.deck_button_rect, 3)

    def drawPlayerOptions(self):
        mousePos = pygame.mouse.get_pos()
        mousePosPlayerOpcions = (mousePos[0] - self.playerOpcionsRect.x, mousePos[1] - self.playerOpcionsRect.y)
        self.playerOpcions.fill((0, 0, 0, 0))
        pygame.draw.rect(self.playerOpcions, (255, 255, 255), self.sortHandRect, 2, border_radius=12)

        if self.sortRankRect.collidepoint(mousePosPlayerOpcions):
            pygame.draw.rect(self.playerOpcions, (200, 170, 0), self.sortRankRect, border_radius=8)
        else:
            pygame.draw.rect(self.playerOpcions, 'orange', self.sortRankRect, border_radius=8)

        if self.sortSuitRect.collidepoint(mousePosPlayerOpcions):
            pygame.draw.rect(self.playerOpcions, (200, 170, 0), self.sortSuitRect, border_radius=8)
        else:
            pygame.draw.rect(self.playerOpcions, 'orange', self.sortSuitRect, border_radius=8)

        self.playerOpcions.blit(self.sortRankText, self.sortRankText.get_rect(center=self.sortRankRect.center))
        self.playerOpcions.blit(self.sortSuitText, self.sortSuitText.get_rect(center=self.sortSuitRect.center))
        sort_title_rect = self.sortTitleText.get_rect(centerx=self.sortHandRect.centerx)
        sort_title_rect.centery = self.sortRankRect.y - (sort_title_rect.height // 2) - 6
        self.playerOpcions.blit(self.sortTitleText, sort_title_rect)

        if len(self.cardsSelectedList) > 0:
            if self.playHandButtonRect.collidepoint(mousePosPlayerOpcions):
                pygame.draw.rect(self.playerOpcions, (0, 0, 139), self.playHandButtonRect, border_radius=12)
            else:
                pygame.draw.rect(self.playerOpcions, 'blue', self.playHandButtonRect, border_radius=12)

            if self.discardButtonRect.collidepoint(mousePosPlayerOpcions):
                pygame.draw.rect(self.playerOpcions, (128, 0, 0), self.discardButtonRect, border_radius=12)
            else:
                pygame.draw.rect(self.playerOpcions, 'red', self.discardButtonRect, border_radius=12)

            self.playerOpcions.blit(self.playHandText,
                                    self.playHandText.get_rect(center=self.playHandButtonRect.center))
            self.playerOpcions.blit(self.discardText, self.discardText.get_rect(center=self.discardButtonRect.center))

        State.screen.blit(self.playerOpcions, self.playerOpcionsRect.topleft)

    def drawDeckPileOverlay(self):
        if self.show_deck_pile:
            overlay = pygame.Surface((1300, 750), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            card_images = State.deckManager.load_card_images(self.playerInfo.levelManager.next_unfinished_sublevel(), self.enhanced_cards)
            suits = [Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS, Suit.SPADES]
            ranks = [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
                     Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
            enhancements = [Enhancement.BASIC, Enhancement.BONUS, Enhancement.GLASS, Enhancement.STEEL,
                            Enhancement.LUCKY]
            start_x, start_y = 100, 100
            spacing_x, spacing_y = 75, 100

            unusable = set()
            for c in self.cardsSelectedList:
                unusable.add((c.suit, c.rank))
            for c in self.hand:
                unusable.add((c.suit, c.rank))
            for c in self.used:
                unusable.add((c.suit, c.rank))

            for row, suit in enumerate(suits):
                for col, rank in enumerate(ranks):
                    img = card_images.get((suit, rank))
                    if img:
                        x = start_x + col * spacing_x
                        y = start_y + row * spacing_y
                        self.screen.blit(img, (x,y))

                    if (suit, rank) in unusable: #or (suit, rank) in deck_selected:
                        rect = pygame.Rect(start_x + col * spacing_x, start_y + row * spacing_y, img.get_width(), img.get_height())
                        self.gray_overlay_(self.screen, rect)

            close_text = self.playerInfo.textFont2.render("Click anywhere to close", True, 'white')
            self.screen.blit(close_text, (start_x, start_y + len(suits) * spacing_y + 20))

    # ----------------------------Input Methods-----------------------------------------------
    def userInput(self, events):
        mousePos = pygame.mouse.get_pos()
        mousePosPlayerOpcions = (mousePos[0] - self.playerOpcionsRect.x, mousePos[1] - self.playerOpcionsRect.y)

        # heat keybind
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_h:  # Press H to activate heat
                self.activateHeat()

        if events.type == pygame.MOUSEBUTTONDOWN:
            mousePos = pygame.mouse.get_pos()

            # Dialogue box logic
            if self.showReviveOption:
                if events.type == pygame.MOUSEBUTTONDOWN:
                    print("DEBUG: Mouse click during game over")
                    if self.noButtonRect.collidepoint(mousePos):
                        print("DEBUG: No button clicked - going to StartState")
                        self.showReviveOption = False
                        self.showRedTint = False
                        self.gameOverTriggered = False

                        # Reset all game state
                        self.playerInfo.amountOfHands = 4
                        self.playerInfo.amountOfDiscards = 4
                        self.playerInfo.roundScore = 0
                        self.playerInfo.playerChips = 0
                        self.playerInfo.playerMultiplier = 0

                        # reset blind
                        if self.playerInfo.levelManager.curLevel:
                            for sublevel in self.playerInfo.levelManager.curLevel:
                                sublevel.finished = False
                            self.playerInfo.levelManager.curSubLevel = self.playerInfo.levelManager.curLevel[0]

                        # Reset deck and hand
                        self.deck = State.deckManager.shuffleDeck(State.deckManager.createDeck(self.playerInfo.levelManager.curSubLevel))
                        self.hand = State.deckManager.dealCards(self.deck, 8, self.playerInfo.levelManager.curSubLevel)
                        self.deck = State.deckManager.shuffleDeck(State.deckManager.createDeck(self.playerInfo.levelManager.next_unfinished_sublevel()))
                        self.hand = State.deckManager.dealCards(self.deck, 8, self.playerInfo.levelManager.next_unfinished_sublevel())
                        self.used = []
                        self.cardsSelectedList = []
                        self.cardsSelectedRect = {}
                        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

                        self.isFinished = True
                        self.nextState = "StartState"
                        self.switchToNormalTheme(force=True)
                        return

                    souls = getattr(self.playerInfo, 'souls', 0)
                    revive_cost = getattr(self.playerInfo, 'reviveCost', 20)
                    has_revived = getattr(self.playerInfo, 'hasRevivedThisBlind', False)

                    if not has_revived and souls >= revive_cost:
                        if self.yesButtonRect.collidepoint(mousePos):
                            if self.handleRevive():
                                return

                return

        if events.type == pygame.QUIT:
            self.isFinished = True
            self.nextState = "StartState"

        # Escape key to quit
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_ESCAPE:
                self.isFinished = True
                self.nextState = "StartState"

        # ---------------- Mouse clicks below ----------------
        if events.type == pygame.MOUSEBUTTONDOWN:
            if self.show_deck_pile:
                self.show_deck_pile = False
                return

            if self.deck_button_rect.collidepoint(mousePos):
                self.show_deck_pile = True


            # added heat logic here
            if self.playHandButtonRect.collidepoint(mousePosPlayerOpcions):
                can_play_hand = (
                        self.playerInfo.amountOfHands > 0 or
                        self.playerInfo.amountOfHands == 0 or
                        (self.playerInfo.isHeatActive and self.playerInfo.heat_level == 3)
                )

                if not self.playHandActive and len(self.cardsSelectedList) > 0 and can_play_hand:
                    self.playHand()

            if self.discardButtonRect.collidepoint(mousePosPlayerOpcions):
                can_discard = (
                        self.playerInfo.amountOfDiscards > 0 or
                        (self.playerInfo.isHeatActive and self.playerInfo.heat_level >= 2)
                )

                if not self.playHandActive and len(self.cardsSelectedList) > 0 and can_discard:
                    if not (self.playerInfo.isHeatActive and self.playerInfo.heat_level >= 2) and self.playerInfo.amountOfDiscards > 0:
                        self.playerInfo.amountOfDiscards -= 1
                    self.discardCards(True)

            if self.sortRankRect.collidepoint(mousePosPlayerOpcions):
                self.sorting = "rank"
                self.SortCards(sort_by="rank")

            if self.sortSuitRect.collidepoint(mousePosPlayerOpcions):
                self.sorting = "suit"
                self.SortCards(sort_by="suit")

            if self.playerInfo.runInfoRect.collidepoint(
                    (mousePos[0] - self.playerInfo.playerInfo2.x, mousePos[1] - self.playerInfo.playerInfo2.y)):
                State.screenshot = self.screen.copy()
                self.isFinished = True
                self.nextState = "RunInfoState"

            # Joker click info
            for joker_obj, joker_rect in self.jokers.items():
                if joker_rect.collidepoint(mousePos):
                    desc_text = self._pretty_joker_description(joker_obj)
                    price = getattr(joker_obj, 'price', None)
                    extra = f" — Price: {price}$" if price is not None else ""
                    print("------------------------------------------------------------")
                    print(f"[JOKER] {joker_obj.name} — {desc_text}{extra}")
                    # Pass onto the sell area

            # Sell
            if self.sell_rect and self.sell_rect.collidepoint(mousePos):
                if not self.joker_for_sell or not isinstance(self.joker_for_sell, tuple) or len(
                        self.joker_for_sell) < 1:
                    print("[GAME] sell clicked but no joker selected")
                    self.sell_rect = None
                    self.use_rect = None
                    self.selected_info = None
                    return

                joker_obj, _ = self.joker_for_sell
                if joker_obj.name in self.playerJokers:
                    self.playerJokers.remove(joker_obj.name)
                elif joker_obj.name in self.playerConsumables:
                    self.playerConsumables.remove(joker_obj.name)
                else:
                    print(f"[GAME] sell: {joker_obj.name} not in playerJokers")

                self.playerInfo.playerMoney += joker_obj.sellPrice()
                self.buy_sound.play()
                self.joker_for_sell = None
                self.joker_for_use = None
                self.selected_info = None
                return

            # Use
            if self.use_rect and self.use_rect.collidepoint(mousePos):
                self.use_sound.play()
                if not self.joker_for_use or not isinstance(self.joker_for_use, tuple) or len(
                        self.joker_for_use) < 1:
                    print("[GAME] use clicked but no joker selected")
                    self.use_rect = None
                    self.selected_info = None
                    return
                joker_obj, _ = self.joker_for_use
                if joker_obj.name in self.playerConsumables:
                    if joker_obj.name in PLANETS and isinstance(joker_obj, PlanetCard):
                        joker_obj.activatePlanet(HAND_SCORES)

                    # Tarot activation and additional logic
                    if joker_obj.name in TAROTS and isinstance(joker_obj, TarotCard):
                        requires_selection = joker_obj.name in [
                            "Silver Chariot", "Magician's Red", "Hierophant Green", "Justice",
                            "Star Platinum", "The World", "The Hanged Man", "Death 13"
                        ]

                        if requires_selection and not self.cardsSelectedList:
                            print(f"Error: {joker_obj.name} requires selected cards but none were chosen!")
                            return

                        result = joker_obj.activateTarot(self.cardsSelectedList, self.hand)
                        print(f"Tarot '{joker_obj.name}' activated with result: {result}")

                        if result and "effect" in result:
                            if result["effect"] == "create_joker":
                                self.handleJudgmentEffect()
                            elif result["effect"] == "create_tarots":
                                self.handleEmperorEffect(result.get("count", 2))
                            elif result["effect"] == "recreate_last_used":
                                self.handleFoolEffect()

                        if joker_obj.name in [
                            "Star Platinum", "The World", "Death 13",
                            "Silver Chariot", "Magician's Red", "Hierophant Green", "Justice"]:
                            self.updateCardImages()
                            self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

                        if joker_obj.name != "The Fool":
                            self.card_usage_history.append(joker_obj.name)
                            self.card_usage_history = self.card_usage_history[-10:]
                            print(f"DEBUG: Added {joker_obj.name} to usage history")

                        if result and "destroyed_cards" in result and result["destroyed_cards"]:
                            self.destroy_sound.play()
                            self.handleDestroyedCards(result)
                        if (result) and ("enhanced_cards" in result) and (result["enhanced_cards"]):
                            for e_enhancement, (e_suit, e_rank) in result["enhanced_cards"]:
                                for s_enhancement, (s_suit, s_rank) in self.enhanced_cards:
                                    if (e_suit, e_rank) == (s_suit, s_rank):
                                        self.enhanced_cards.remove((s_enhancement, (s_rank, s_suit)))
                                        break
                                else:
                                    self.enhanced_cards += result["enhanced_cards"]
                            self.use_sound.play()
                            self.updateCardImages()
                            self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

                        # Remove from inventory
                    self.playerConsumables.remove(joker_obj.name)
                    print(f"DEBUG: Removed {joker_obj.name} from playerConsumables")
                    print(f"DEBUG: playerConsumables after removal: {self.playerConsumables}")
                else:
                    print(f"[GAME] use: {joker_obj.name} not in playerConsumables")
                    print(f"DEBUG: Available consumables: {self.playerConsumables}")

                self.joker_for_sell = None
                self.joker_for_use = None
                self.selected_info = None
                return

            # TODO: if we make a use sound, play it here
            # -- Consumable click info --
            # Owned consumables: check positions rendered by GameState
            if not self.consumables:
                self.drawConsumables()
            if not self.jokers:
                self.drawJokers()
            joker_objects = self.consumables.copy()
            joker_objects.update(self.jokers.copy())
            for joker_obj, joker_rect in joker_objects.items():
                if joker_rect.collidepoint(mousePos) and not (self.joker_for_sell or self.joker_for_use):
                    # print(f"DEBUG: Clicked on joker/consumable: {joker_obj.name}")
                    # print(f"DEBUG: Type: {type(joker_obj)}")
                    desc_text = joker_obj.description
                    price = joker_obj.price
                    name = joker_obj.name
                    usable = True if isinstance(joker_obj, PlanetCard) or (
                        isinstance(joker_obj, TarotCard)) else False
                    self.joker_for_sell = (joker_obj, joker_rect)
                    self.joker_for_use = (joker_obj, joker_rect) if usable else None
                    self.selected_info = {'name': name, 'desc': desc_text, 'price': price, 'can_buy': False,
                                          'usable': usable}
                    # print(f"DEBUG: Set joker_for_use to: {self.joker_for_use[0].name if self.joker_for_use else None}")
                    return
            else:
                self.joker_for_sell = None
                self.joker_for_use = None

        # Pass input to playerInfo and debugState
        self.playerInfo.userInput(events)
        self.debugState.userInput(events)
        self.userInputCards(events)

    def userInputCards(self, events):
        if events.type == pygame.MOUSEBUTTONDOWN and not self.playHandActive:
            mousePos = pygame.mouse.get_pos()
            # Iterate in reverse to select the top-most card first
            for card in reversed(list(self.cards.keys())):
                if self.cards[card].collidepoint(mousePos):
                    if not card.isSelected:
                        if len(self.cardsSelectedList) < 5:
                            card.isSelected = True
                            self.cards[card].y -= 50
                            self.cardsSelectedList.append(card)
                            self.select_sfx.play()
                    else:
                        card.isSelected = False
                        self.cards[card].y += 50
                        self.cardsSelectedList.remove(card)
                        self.deselect_sfx.play()
                    return  # Stop after interacting with one card

    # DONE (TASK 7) - Rewrite this function so that it calculates the player's gold reward *recursively*.
    #   The recursion should progress through each step of the reward process (base reward, bonus for overkill, etc.)
    #   by calling itself with updated parameters or stages instead of using loops.
    #   Each recursive call should handle a single part of the reward logic, and the final base case should
    #   return the total combined reward once all calculations are complete.
    #   The function must include:
    #     - Base gold depending on blind type (SMALL=4, BIG=8, BOSS=10)
    #     - Recursive calculation of the overkill bonus (based on how much score exceeds the target)
    #     - A clear base case to stop recursion when all parts are done
    #   Avoid any for/while loops — recursion alone must handle the repetition.
    def calculate_gold_reward(self, playerInfo, stage=0):
        # Base gold
        sm_gold: int = 4
        big_gold: int = 8
        boss_gold: int = 10


        # Base case
        if stage > 0:
            score = playerInfo.score
            target = playerInfo.levelManager.curSubLevel.blind.value
            bonus = ((score - target) / target) * 5

            if bonus < 0:
                bonus = 0
            if bonus > 5:
                bonus = 5


            return int(round(bonus, 0)) + stage


        # The one recursive case lol
        blind = playerInfo.levelManager.curSubLevel.blind
        match blind.value:
            case Blind.SMALL.value:
                return self.calculate_gold_reward(playerInfo, sm_gold)
            case Blind.BIG.value:
                return self.calculate_gold_reward(playerInfo, big_gold)
            case Blind.BOSS.value:
                return self.calculate_gold_reward(playerInfo, boss_gold)

        # Failsafe
        return self.calculate_gold_reward(playerInfo, sm_gold)



    def updateCards(self, posX, posY, cardsDict, cardsList, scale=1.5, spacing=90, baseYOffset=-20, leftShift=40):
        cardsDict.clear()
        for i, card in enumerate(cardsList):
            w, h = card.image.get_width(), card.image.get_height()
            new_w, new_h = int(w * scale), int(h * scale)
            card.scaled_image = pygame.transform.scale(card.image, (new_w, new_h))
            x = posX + i * spacing - leftShift
            y = posY + baseYOffset
            if getattr(card, "isSelected", False):
                y -= 50
            cardsDict[card] = pygame.Rect(x, y, new_w, new_h)

    # DONE (TASK 2) - Implement a basic card-sorting system without using built-in sort functions.
    #   Create a 'suitOrder' list (Hearts, Clubs, Diamonds, Spades), then use nested loops to compare each card
    #   with the ones after it. Depending on the mode, sort by rank first or suit first, swapping cards when needed
    #   until the entire hand is ordered correctly.
    def SortCards(self, sort_by: str = "suit"):
        # While programming this task, the code editor suggested I use random.shuffle
        # The voices are begging me to use bogosort
        suitOrder = [Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS, Suit.SPADES]   # Define the order of suits

        if sort_by == "rank":
            sort_suits = False
        elif sort_by == "suit":
            sort_suits = True
        elif sort_by == "":
            return
        else:
            raise IOError("sort_by must be of 'rank', 'suit' or an empty string ('')")


        hand_buffer = self.hand.copy()
        is_sorted = False
        while not is_sorted:
            is_sorted = True
            for i in range(len(hand_buffer)):
                card = hand_buffer[i]
                for j in range(i, len(hand_buffer)):
                    card_rabbit = hand_buffer[j]
                    if card.rank.value < card_rabbit.rank.value:
                        popped_card = hand_buffer.pop(i)
                        hand_buffer.append(popped_card)
                        is_sorted = False
                        break

        full_hand = []
        if sort_suits:
            sorted_suits = []
            for suit in suitOrder:
                suit_group = []
                for card in hand_buffer:
                    if card.suit == suit:
                        suit_group.append(card)
                sorted_suits.append(suit_group)

            for suits_group in sorted_suits:
                for card in suits_group:
                    full_hand.append(card)
        else:
            full_hand = hand_buffer


        self.hand = full_hand

        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

    def checkHoverCards(self):
        mousePos = pygame.mouse.get_pos()
        for card, rect in self.cards.items():
            if rect.collidepoint(mousePos):
                break
    
    def drawCardTooltip(self):
        mousePos = pygame.mouse.get_pos()
        for card, rect in self.cards.items():
            if rect.collidepoint(mousePos):
                tooltip_text = f"{card.rank.name.title()} of {card.suit.name.title()} ({card.chips} Chips)"
                font = self.playerInfo.textFont1
                if self.playerInfo.levelManager.curSubLevel.bossLevel == "The Mark":
                    if card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
                        text_surf = font.render("???", False, 'White')
                    else:
                        text_surf = font.render(tooltip_text, False, 'white')
                elif self.playerInfo.levelManager.curSubLevel.bossLevel == "The House":
                    if card.faceDown:
                        text_surf = font.render("???", False, 'White')
                    else:
                        text_surf = font.render(tooltip_text, False, 'white')
                else:
                    text_surf = font.render(tooltip_text, False, 'white')
                padding = 6
                tooltip_w, tooltip_h = text_surf.get_width() + padding * 2, text_surf.get_height() + padding * 2
                tooltip_surf = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
                pygame.draw.rect(tooltip_surf, (0, 0, 0, 180), tooltip_surf.get_rect(), border_radius=6)
                tooltip_surf.blit(text_surf, (padding, padding))
                tooltip_x = rect.x + (rect.width - tooltip_w) // 2
                tooltip_y = rect.y - tooltip_h - 10
                self.screen.blit(tooltip_surf, (tooltip_x, tooltip_y))
                break

    # drawCardToolTip, but with only joker-style objects (Jokers and Consumables)
    def drawJokerTooltip(self):
        if self.gameOverTriggered:
            return

        mousePos = pygame.mouse.get_pos()
        joker_objects = self.jokers.copy()
        joker_objects.update(self.consumables)
        for joker_obj, joker_rect in joker_objects.items():
            if joker_rect.collidepoint(mousePos) and \
                    (isinstance(joker_obj, Jokers) or isinstance(joker_obj, PlanetCard) or isinstance(joker_obj, TarotCard)):

                if isinstance(joker_obj, Jokers):
                    tooltip_text = f"{joker_obj.name}\n{self._pretty_joker_description(joker_obj)}"
                else:
                    tooltip_text = f"{joker_obj.name}\n{joker_obj.description}"
                font = self.playerInfo.textFont1
                # If we made any boss blinds reliant on deactivating jokers those would go here

                # - Text wrapping -
                tooltip_wrap_char_amount = 20
                cur_tooltip_line = ""
                text_surf_lines = []
                total_width = 0
                total_height = 0
                max_len, max_len_id, cur_id = 0, 0, 0
                offset = 0
                for i in range(len(tooltip_text)):
                    char = tooltip_text[i]
                    cur_tooltip_line += char if char != '\n' else ' '
                    if ((char == '\n') and len(cur_tooltip_line) > 1) or (len(cur_tooltip_line) == tooltip_wrap_char_amount - 1)\
                            or (i == len(tooltip_text) - 1):
                        next_tooltip_line = ""
                        if i != len(tooltip_text) - 1:
                            for j in range(len(cur_tooltip_line)):
                                if cur_tooltip_line[len(cur_tooltip_line) - j - 1] in {' ', '\n'}:
                                    next_tooltip_line = cur_tooltip_line[(len(cur_tooltip_line) - j - 1):]
                                    cur_tooltip_line = cur_tooltip_line[:len(cur_tooltip_line) - j - 1]
                                    break

                        if len(cur_tooltip_line) > max_len:
                            max_len = len(cur_tooltip_line)
                            max_len_id = cur_id

                        cur_surf_line = font.render(cur_tooltip_line, False, 'white')
                        total_height += cur_surf_line.get_height()

                        text_surf_lines.append(cur_surf_line)
                        cur_tooltip_line = next_tooltip_line
                        cur_id += 1

                total_width = text_surf_lines[max_len_id].get_width()

                padding = 6
                tooltip_w, tooltip_h = total_width + padding * 2, total_height + padding * 2
                tooltip_surf = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
                pygame.draw.rect(tooltip_surf, (0, 0, 0, 180), tooltip_surf.get_rect(), border_radius=6)

                for i in range(len(text_surf_lines)):
                    surf_line = text_surf_lines[i]
                    tooltip_surf.blit(surf_line, (padding, padding + (i * 25)))

                tooltip_x = joker_rect.x + (joker_rect.width - tooltip_w) // 2
                tooltip_y = joker_rect.y + tooltip_h + 15
                self.screen.blit(tooltip_surf, (tooltip_x, tooltip_y))
                break
    
    # -------- Play Hand Logic -----------
    def playHand(self):
        target_score = self.playerInfo.levelManager.curSubLevel.score
        heat_play = self.playerInfo.isHeatActive and self.playerInfo.heat_level == 3
        if self.playerInfo.amountOfHands <= 0 and not heat_play:
            if self.playerInfo.roundScore < target_score and not self.gameOverTriggered:
                self.gameOverTriggered = True
                pygame.mixer.music.stop()
                self.gameOverSound.play()
                self.showRedTint = True

                # Reset your souls after attempting to revive in the same blind again
                if getattr(self.playerInfo, 'hasRevivedThisBlind', False):
                    self.playerInfo.souls = 0

                for alpha in range(0, 180, 10):
                    self.redAlpha = alpha
                    self.draw()
                    tint = pygame.Surface((1300, 750), pygame.SRCALPHA)
                    tint.fill((255, 0, 0, alpha))
                    self.screen.blit(tint, (0, 0))
                    pygame.display.update()
                    pygame.time.wait(80)


                pygame.time.wait(1200)

                self.showReviveOption = True
                self.drawGameOverScreen()
                self.draw()
                return

        if not (self.playerInfo.isHeatActive and self.playerInfo.heat_level == 3):
            self.playerInfo.amountOfHands -= 1

        hand_name = evaluate_hand(self.cardsSelectedList)
        self.playedHandName = hand_name
        self.playedHandNameList.append(hand_name)

        # Base values from HAND_SCORES
        score_info = HAND_SCORES.get(hand_name, {"chips": 0, "multiplier": 1})
        hand_chips = score_info.get("chips", 0)
        hand_mult = score_info.get("multiplier", 1)

        # Prepare helpers
        sel = list(self.cardsSelectedList)
        # group by rank value and by suit
        by_rank = {}
        for c in sel:
            by_rank.setdefault(c.rank.value, []).append(c)
        by_suit = {}
        for c in sel:
            by_suit.setdefault(c.suit, []).append(c)

        used_cards = []

        # Helper: find straight sequence in a list of ranks -> returns list of rank values
        def find_straight_ranks(ranks_set):
            vals = sorted(set(ranks_set))
            # include low-Ace (1) if Ace present
            if 14 in vals:
                vals_with_ace_low = sorted(set(vals + [1]))
            else:
                vals_with_ace_low = vals
            seq_start = None
            consec = 1
            best_seq = []
            arr = vals_with_ace_low
            for i in range(len(arr)):
                if i == 0:
                    consec = 1
                    seq_start = arr[0]
                    cur_seq = [arr[0]]
                else:
                    if arr[i] == arr[i-1]:
                        continue
                    if arr[i] == arr[i-1] + 1:
                        consec += 1
                        cur_seq.append(arr[i])
                    else:
                        consec = 1
                        cur_seq = [arr[i]]
                    if consec >= 5:
                        best_seq = cur_seq[-5:]
                        break
            return best_seq  # may be empty

        # Determine used Cards per hand type
        if hand_name == "Straight Flush":
            # find suit with >=5 then detect straight inside that suit
            for suit, cards in by_suit.items():
                if len(cards) >= 5:
                    suit_ranks = [c.rank.value for c in cards]
                    seq = find_straight_ranks(suit_ranks)
                    if seq:
                        # pick the Cards matching those ranks and suit
                        for rv in seq:
                            # map low-Ace (1) back to 14 if needed
                            pick_val = 14 if rv == 1 and not any(c.rank.value == 1 for c in cards) else rv
                            # find card with that rank value (prefer exact match)
                            for c in cards:
                                if c.rank.value == pick_val or (rv == 1 and c.rank.value == 14):
                                    used_cards.append(c)
                                    break
                        break

        elif hand_name == "Four of a Kind":
            four_rank = None
            for rv, lst in by_rank.items():
                if len(lst) >= 4:
                    if four_rank is None or rv > four_rank:
                        four_rank = rv
            if four_rank:
                used_cards = by_rank[four_rank][:4]

        elif hand_name == "Full House":
            three_rank = None
            pair_rank = None
            for rv in sorted(by_rank.keys(), reverse=True):
                if len(by_rank[rv]) >= 3 and three_rank is None:
                    three_rank = rv
            for rv in sorted(by_rank.keys(), reverse=True):
                if rv != three_rank and len(by_rank[rv]) >= 2:
                    pair_rank = rv
                    break
            if three_rank and pair_rank:
                used_cards = by_rank[three_rank][:3] + by_rank[pair_rank][:2]
            else:
                # fallback: if multiple triples exist, use highest triple + next triple (as pair)
                triples = [rv for rv, lst in by_rank.items() if len(lst) >= 3]
                if len(triples) >= 2:
                    t_sorted = sorted(triples, reverse=True)
                    used_cards = by_rank[t_sorted[0]][:3] + by_rank[t_sorted[1]][:2]

        elif hand_name == "Flush":
            flush_suit = None
            for suit, lst in by_suit.items():
                if len(lst) >= 5:
                    flush_suit = suit
                    break
            if flush_suit:
                # pick top 5 highest rank Cards of that suit
                cards_sorted = sorted(by_suit[flush_suit], key=lambda c: c.rank.value, reverse=True)
                used_cards = cards_sorted[:5]

        elif hand_name == "Straight":
            seq = find_straight_ranks([c.rank.value for c in sel])
            if seq:
                # for each rank in seq pick one available card with that rank (prefer highest suit not important)
                for rv in seq:
                    pick_val = 14 if rv == 1 and any(c.rank.value == 14 for c in sel) else rv
                    for c in sel:
                        if c.rank.value == pick_val or (rv == 1 and c.rank.value == 14):
                            used_cards.append(c)
                            break

        elif hand_name == "Three of a Kind":
            three_rank = None
            for rv in sorted(by_rank.keys(), reverse=True):
                if len(by_rank[rv]) >= 3:
                    three_rank = rv
                    break
            if three_rank:
                used_cards = by_rank[three_rank][:3]

        elif hand_name == "Two Pair":
            pairs = [rv for rv, lst in by_rank.items() if len(lst) >= 2]
            if pairs:
                top_pairs = sorted(pairs, reverse=True)[:2]
                for rv in top_pairs:
                    used_cards += by_rank[rv][:2]

        elif hand_name == "One Pair":
            pair_rank = None
            for rv in sorted(by_rank.keys(), reverse=True):
                if len(by_rank[rv]) >= 2:
                    pair_rank = rv
                    break
            if pair_rank:
                used_cards = by_rank[pair_rank][:2]

        else:  # High Card or fallback
            # pick single highest card
            best = max(sel, key=lambda c: c.rank.value)
            used_cards = [best]

        # List of not-selected cards
        held_cards = []
        for c in list(self.hand):
            if c not in sel:
                held_cards.append(c)

        # Sum chips of only the used Cards
        card_chips_sum = 0
        for c in used_cards:
            card_chips_sum += c.chips
            # Card scoring enhancements
            # TODO: Verify if this match statement works or if you need to index the <.value>s
            match c.enhancement:
                case Enhancement.BONUS:
                    card_chips_sum += 30
                case Enhancement.MULT:
                    hand_mult += 4
                case Enhancement.GLASS:
                    hand_mult *= 2
                    if random.randint(1, 4) == 1:
                        self.hand.remove(c)
                        self.deck.remove(c)
                case Enhancement.LUCKY:
                    if random.randint(1, 5) == 1:
                        hand_mult += 20
                    if random.randint(1, 15) == 1:
                        self.playerInfo.playerMoney += 20

        # total chips for display = base hand value + sum of used Cards' chips
        total_chips = hand_chips + card_chips_sum

        # ----------------- Apply Card Enhancements -----------------
        # DONE (BONUS): Apply the effects for every card enhancement that influences scoring
        #   List of card enhancements that apply in scoring (above):
        #   - Bonus Cards: Give an additional +30 chips when scored
        #   - Mult Cards: Give an additional +4 Mult when scored
        #   - Glass Cards: Give *2 mult when scored, with a 1 in 4 chance to self-destruct,
        #       removing them from your deck for the rest of the run
        #   - Lucky Cards: When scored, have a...
        #       > 1 in 5 chance to give +20 mult when scored
        #       > 1 in 15 chance to give $20
        #       (Both effects are triggered independently and may occur simultaneously)
        #   List of card enhancements that apply after scoring (below):
        #   - Steel Cards: Give *1.5 mult when held in hand
        #   - Gold Cards: Give $3 if held in hand AT THE END OF THE ROUND
        #   List of card enhancements that definitely go somewhere else
        #   - Wild Cards: Are considered of every suit simultaneously (HandEvaluator.py)
        # TODO: Check if works
        # -----------------------------------------------------------------

        # ------------------ Effects for Held Cards ------------------------
        # TODO: Same thing as above with the selected cards, check if the match statement actually works
        for c in held_cards:
            match c.enhancement:
                case Enhancement.STEEL:
                    hand_mult *= 1.5

        # ------------------- Apply Joker effects -------------------
        owned = set(self.playerJokers)
        # TODO (TASK 5.2): Let the Joker mayhem begin! Implement each Joker’s effect using the Joker table as reference.
        #   Follow this structure for consistency:
        #   if "joker card name" in owned:
        #       # Apply that Joker’s effect
        #       self.activated_jokers.add("joker card name")
        #   The last line ensures the Joker is visibly active and its effects are properly applied.
        # Variables for readability
        two = Rank.TWO
        three = Rank.THREE
        four = Rank.FOUR
        five = Rank.FIVE
        six = Rank.SIX
        seven = Rank.SEVEN
        eight = Rank.EIGHT
        nine = Rank.NINE
        ten = Rank.TEN
        jack = Rank.JACK
        queen = Rank.QUEEN
        king = Rank.KING
        ace = Rank.ACE
        # Joker abilities are below

        procrastinate = False
        bonus_802 = False

        if "The Joker" in owned:
            hand_mult += 4
            self.activated_jokers.add("The Joker")

        if "Michael Myers" in owned:
            random_mult = random.randint(0, 23)
            hand_mult += random_mult
            self.activated_jokers.add("Michael Myers")

        if "Fibonacci" in owned:
            funny_cards = [two, three, five, eight, ace]
            used = False
            for card in self.cardsSelectedList:
                if card.rank in funny_cards:
                    hand_mult += 8
                    used = True
            if used:
                self.activated_jokers.add("Fibonacci")

        if "Gauntlet" in owned:
            total_chips += 250
            self.playerInfo.amountOfHands -= 2
            self.activated_jokers.add("Gauntlet")

        if "Ogre" in owned:
            joker_amount_mult = len(self.playerJokers) * 3
            hand_mult += joker_amount_mult
            self.activated_jokers.add("Ogre")

        if "Straw Hat" in owned:
            hands_played = max(0, len(self.playedHandNameList) - 1)
            bonus = max(0, 100 - (5 * hands_played))
            total_chips += bonus
            self.activated_jokers.add("Straw Hat")
            print("ONE PIECEEEEEE, THE ONE PIECE IS REAAAALLLLL")

        if "Hog Rider" in owned:
            if hand_name == "Straight":
                total_chips += 100
            self.activated_jokers.add("Hog Rider")

        if "? Block" in owned and len(self.cardsSelectedList) == 4:
            total_chips += 4
            self.activated_jokers.add("? Block")

        if "Hogwarts" in owned:
            used = False
            for card in self.cardsSelectedList:
                if card.rank == ace:
                    hand_mult += 4
                    total_chips += 20
            if used:
                self.activated_jokers.add("Hogwarts")

        if "802" in owned:
            bonus_802 = True
            self.activated_jokers.add("802")


        # -------------------  HEAT EFFECTS  -------------------
        if self.playerInfo.isHeatActive:
            heat_level = self.playerInfo.heat_level

            if heat_level == 1:
                hand_mult *= 2
                print("HEAT BONUS: 2x multiplier applied!")

            elif heat_level == 2:
                hand_mult = int(hand_mult * 1.2)
                total_chips += 40
                print("HEAT BONUS: 1.2x multiplier + 40 chips!")

            elif heat_level == 3:
                hand_mult = int(hand_mult * 1.8)
                total_chips += 80
                print("HEAT BONUS: 1.8x multiplier + 80 chips!")
        # ---------------------------------------------------------------

        # ------------------ Finalize Hand Scoring ------------------
        # commit modified player multiplier and chips
        self.playerInfo.playerMultiplier = hand_mult
        self.playerInfo.playerChips = total_chips
        self.playerInfo.curHandOfPlayer = hand_name
        self.playerInfo.curHandText = self.playerInfo.textFont1.render(self.playerInfo.curHandOfPlayer, False, 'white')

        # compute amount that will be added to round when timer expires
        added_to_round = total_chips * hand_mult
        # Procrastination doubles the final hand's addition
        if 'procrastinate' in locals() and procrastinate:
            added_to_round *= 2

        if bonus_802:
            added_to_round *= 2
        self.pending_round_add = added_to_round  # defer actual addition until timer ends

        # prepare on-screen feedback
        self.playedHandTextSurface = self.playerInfo.textFont1.render(hand_name, True, 'yellow')
        score_breakdown_text = f"(Hand: {hand_chips} + Cards: {card_chips_sum}) Chips | x{hand_mult} Mult -> +{added_to_round}"
        self.scoreBreakdownTextSurface = self.playerInfo.textFont2.render(score_breakdown_text, True, 'white')

        self.playHandStartTime = pygame.time.get_ticks()
        self.playHandActive = True
        self.cardsSelectedRect.clear()

        start_x, start_y, spacing = 20, 20, 95
        for i, card in enumerate(self.cardsSelectedList):
            w, h = card.scaled_image.get_width(), card.scaled_image.get_height()
            self.cardsSelectedRect[card] = pygame.Rect(start_x + i * spacing, start_y, w, h)

        # ------------- Apply Effects for Winning Hand --------------
        if added_to_round > self.playerInfo.levelManager.curSubLevel.score:
            for c in held_cards:
                match c.enhancement:
                    case Enhancement.GOLD:
                        self.playerInfo.playerMoney += 3

    def handleDestroyedCards(self, result):
        destroyed_cards = []

        # Destroys them mfs
        if "destroyed_cards" in result and result["destroyed_cards"]:
            destroyed_cards.extend(result["destroyed_cards"])
            print(f"DEBUG: Found {len(destroyed_cards)} destroyed cards in result")

        if not destroyed_cards:
            print("DEBUG: No destroyed cards found in result")
            return

        print("DEBUG: Cards to destroy:")
        for card in destroyed_cards:
            print(f"  - {card.rank.name} of {card.suit.value} (in hand: {card in self.hand}, in deck: {card in self.deck})")

        cards_removed = []
        for card in destroyed_cards:
            if card in self.hand:
                self.hand.remove(card)
                cards_removed.append(f"{card.rank.name} of {card.suit.value}")
                print(f"SUCCESS: Card {card.rank.name} of {card.suit.value} was destroyed and removed from hand")
            elif card in self.deck:
                self.deck.remove(card)
                print(f"SUCCESS: Card {card.rank.name} of {card.suit.value} was destroyed and removed from deck")
            else:
                print(f"ERROR: Card {card.rank.name} of {card.suit.value} not found in hand or deck")

        for card in destroyed_cards:
            if card in self.cardsSelectedList:
                self.cardsSelectedList.remove(card)
                print(f"DEBUG: Removed {card.rank.name} of {card.suit.value} from cardsSelectedList")

        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

        if cards_removed:
            print(f"SUCCESS: Destroyed and removed: {', '.join(cards_removed)}")
            print(f"DEBUG: Hand now has {len(self.hand)} cards")
        else:
            print("ERROR: No cards were actually removed")

    def updateCardImages(self):
        print("DEBUG: Force updating all card images")

        card_images = State.deckManager.load_card_images(self.playerInfo.levelManager.next_unfinished_sublevel(), self.enhanced_cards)

        for card in self.hand:
            key = (card.suit, card.rank)
            if key in card_images:
                card.image = card_images[key]
                original_w, original_h = card.image.get_size()
                scaled_w = int(original_w * 1.2)
                scaled_h = int(original_h * 1.2)
                card.scaled_image = pygame.transform.scale(card.image, (scaled_w, scaled_h))

        self.cards.clear()
        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

        print("DEBUG: Force update completed")

    def handleJudgmentEffect(self):
        """Handle Judgment tarot - create random joker"""
        # Check if player has room for more jokers (max 5)
        if len(self.playerJokers) < 5:
            available_jokers = [j for j in self.jokerDeck if j.name not in self.playerJokers]
            if available_jokers:
                new_joker = random.choice(available_jokers)
                self.playerJokers.append(new_joker.name)
                # Update PlayerInfo display
                self.playerInfo.curAmountJoker = str(len(self.playerJokers))
                print(f"Judgment created: {new_joker.name}")
            else:
                print("Judgment: No available jokers to create")
        else:
            print("Judgment: No room for more jokers (max 5)")

    def handleEmperorEffect(self, count=2):
        available_slots = 5 - len(self.playerConsumables)

        if available_slots > 0:
            available_tarots = [t for t in TAROTS.values() if t.name not in self.playerConsumables and t.name != "The Emperor"]
            num_to_create = min(available_slots, len(available_tarots), count)

            created_tarots = []
            for _ in range(num_to_create):
                if available_tarots:
                    new_tarot = random.choice(available_tarots)
                    self.playerConsumables.append(new_tarot.name)
                    created_tarots.append(new_tarot.name)
                    available_tarots.remove(new_tarot)
                    print(f"The Emperor created: {new_tarot.name}")

            if created_tarots:
                print(f"The Emperor created {len(created_tarots)} tarot(s)")
            else:
                print("The Emperor: No available tarots to create")
        else:
            print("The Emperor: No room for more consumables (max 5)")

    def handleFoolEffect(self):
        if len(self.playerConsumables) < 5:
            for card_name in reversed(self.card_usage_history):
                if card_name != "The Fool" and (card_name in TAROTS or card_name in PLANETS):
                    if card_name not in self.playerConsumables:
                        self.playerConsumables.append(card_name)
                        print(f"The Fool recreated: {card_name}")
                        return
            print("The Fool: No recent usable card found in history")
        else:
            print("The Fool: No room for more consumables (max 5)")

    def drawGameOverScreen(self):
       #Back ground, going change ts later
        pygame.draw.rect(self.screen, (30, 30, 50), self.dialogBoxRect, border_radius=12)
        pygame.draw.rect(self.screen, (80, 80, 100), self.dialogBoxRect, 3, border_radius=12)

        mouse_pos = pygame.mouse.get_pos()

        souls = getattr(self.playerInfo, 'souls', 0)
        revive_cost = getattr(self.playerInfo, 'reviveCost', 20)
        has_revived = getattr(self.playerInfo, 'hasRevivedThisBlind', False)


        if has_revived:
            question_text = self.playerInfo.textFont2.render("Already revived this blind!", True, (255, 150, 150))
            souls_text = self.playerInfo.textFont2.render("One revive per blind allowed", True, (200, 150, 150))
        elif souls >= revive_cost:
            question_text = self.playerInfo.textFont2.render(f"Revive for {revive_cost} Souls?", True, (255, 255, 255))
            souls_text = self.playerInfo.textFont2.render(f"You have {souls} souls", True, (200, 200, 100))
        else:
            question_text = self.playerInfo.textFont2.render("Not enough souls to revive", True, (255, 150, 150))
            souls_text = self.playerInfo.textFont2.render(f"Need {revive_cost}, you have {souls}", True, (200, 150, 150))
        center_x = self.dialogBoxRect.centerx
        buttons_y = self.dialogBoxRect.y + 120

        self.yesButtonRect = pygame.Rect(center_x - 110, buttons_y, 100, 50)
        self.noButtonRect = pygame.Rect(center_x + 10, buttons_y, 100, 50)


        if not has_revived and souls >= revive_cost:
            yes_color = (0, 200, 0) if self.yesButtonRect.collidepoint(mouse_pos) else (0, 100, 0)
            pygame.draw.rect(self.screen, yes_color, self.yesButtonRect, border_radius=8)
            yes_text = self.playerInfo.textFont2.render("YES", True, (255, 255, 255))
            self.screen.blit(yes_text, (self.yesButtonRect.centerx - yes_text.get_width() // 2, self.yesButtonRect.centery - yes_text.get_height() // 2))

        no_color = (200, 0, 0) if self.noButtonRect.collidepoint(mouse_pos) else (150, 0, 0)
        pygame.draw.rect(self.screen, no_color, self.noButtonRect, border_radius=8)
        no_text = self.playerInfo.textFont2.render("NO", True, (255, 255, 255))
        self.screen.blit(no_text, (self.noButtonRect.centerx - no_text.get_width() // 2, self.noButtonRect.centery - no_text.get_height() // 2))

        self.screen.blit(question_text,(self.dialogBoxRect.centerx - question_text.get_width() // 2, self.dialogBoxRect.y + 30))
        self.screen.blit(souls_text,(self.dialogBoxRect.centerx - souls_text.get_width() // 2, self.dialogBoxRect.y + 70))

        pygame.display.update()


    def handleRevive(self):
        souls = getattr(self.playerInfo, 'souls', 0)
        revive_cost = getattr(self.playerInfo, 'reviveCost', 20)
        has_revived = getattr(self.playerInfo, 'hasRevivedThisBlind', False)

        print(f"DEBUG handleRevive: souls={souls}, cost={revive_cost}, has_revived={has_revived}")

        # Check if player has enough souls AND hasn't revived this blind yet
        if souls >= revive_cost and not has_revived:
            self.gameOverTriggered = False
            self.playerInfo.souls -= revive_cost
            self.playerInfo.hasRevivedThisBlind = True  # Mark as revived for this blind
            self.playerInfo.amountOfHands = 2
            self.playerInfo.amountOfDiscards = 2
            self.showReviveOption = False
            self.showRedTint = False


            self.draw()
            pygame.display.update()

            print("DEBUG: Resuming music after revive...")

            if self.isBossActive:
                print("DEBUG: Force playing boss music")
                self.bossMusicPlaying = False
                self.switchToBossTheme()
            else:
                print("DEBUG: Force playing normal music")
                self.bossMusicPlaying = True
                self.switchToNormalTheme()

            print(f"Revived! {self.playerInfo.souls} souls remaining")
            return True

        elif has_revived:
            print("DEBUG: Already revived this blind - resetting souls to zero")
            self.playerInfo.souls = 0

        print(f"DEBUG: Revive failed - souls: {souls}, cost: {revive_cost}, has_revived: {has_revived}")
        return False


    def activateHeat(self):
        if self.playerInfo.heat_level > 0 and not self.playerInfo.isHeatActive:
            self.playerInfo.isHeatActive = True
            print(f"HEAT ACTIVATED: Level {self.playerInfo.heat_level}!")

            if self.playerInfo.heat_level == 3:
                self.playerInfo.heatDuration = 600
                print("HEAT ACTIVATED: Unlimited hands and discards for 10 seconds!")
            elif self.playerInfo.heat_level == 2:
                self.playerInfo.heatDuration = 300
                print("HEAT ACTIVATED: Unlimited discards for 5 seconds!")
            elif self.playerInfo.heat_level == 1:
                self.playerInfo.heatDuration = 300
                print("HEAT ACTIVATED: 2x Multiplier for 5 seconds!")

            self.playerInfo.heat = 0

    def check_heat_level_up(self):
        if self.playerInfo.heat >= 100 and self.playerInfo.heat_level < 3:
            self.playerInfo.heat_level += 1
            self.playerInfo.heat = 0
            print(f"HEAT LEVEL UP! Now at level {self.playerInfo.heat_level}")

            self.show_heat_level_up_effect()

    def show_heat_level_up_effect(self):
        for alpha in range(0, 100, 20):
            flash = pygame.Surface((1300, 750), pygame.SRCALPHA)
            flash.fill((255, 100, 100, alpha))
            self.screen.blit(flash, (0, 0))
            pygame.display.update()
            pygame.time.wait(50)

        # Show level up text
        level_text = self.playerInfo.textFont1.render(f"HEAT LEVEL {self.playerInfo.heat_level}!", True, (255, 255, 0))
        text_rect = level_text.get_rect(center=(650, 375))

        # Background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 200), bg_surface.get_rect(), border_radius=8)

        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(level_text, text_rect)
        pygame.display.update()
        pygame.time.wait(1000)


    # DONE (TASK 4) - The function should remove one selected card from the player's hand at a time, calling itself
    #   again after each removal until no selected cards remain (base case). Once all cards have been
    #   discarded, draw new cards to refill the hand back to 8 cards. Use helper functions but AVOID using
    #   iterations (no for/while loops) — the recursion itself must handle repetition. After the
    #   recursion finishes, reset card selections, clear any display text or tracking lists, and
    #   update the visual layout of the player's hand.
    def discardCards(self, removeFromHand: bool):
        if removeFromHand:  # Recursive cases
            if len(self.cardsSelectedList) > 0:  # If it isn't an empty hand, keep removing a card from the hand
                card_to_remove = self.cardsSelectedList.pop()
                self.hand.remove(card_to_remove)
                self.used.append(card_to_remove)
                self.discardCards(removeFromHand=True)

            self.discardCards(False) # If the hand is now empty, go into the next part of the loop

        if len(self.hand) < 8:  # Alternate recursive case: fill the deck back up
            new_card = self.deck.pop()
            self.hand.append(new_card)
            self.discardCards(removeFromHand=False)

        # Base case
        self.cardsSelectedRect = {}
        self.playedHandNameList = ['']
        self.SortCards(self.sorting)
        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)


