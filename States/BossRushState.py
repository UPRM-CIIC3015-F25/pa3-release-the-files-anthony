from States.GameState import GameState
from States.Core.StateClass import State
from Levels.SubLevel import SubLevel, Blind
import pygame
import random
import os

BOSS_RUSH_BOSSES = [
    {
        "name": "Champion Gundyr",
        "score": 700,
        "theme": "gundyr.mp3",
        "background": "Graphics/Backgrounds/boss_rush/GundyrBG.png",
        "ability": "aggression"
    },
    {
        "name": "Artorias",
        "score": 2500,
        "theme": "artorias.mp3",
        "background": "Graphics/Backgrounds/boss_rush/Artorias.png",
        "ability": "disables_random_joker"
    },
    {
        "name": "Sir Alonne",
        "score": 5000,
        "theme": "sir_alonnes_theme.mp3",
        "background": "graphics/backgrounds/boss_rush/sir_alonne.png",
        "ability": "honorable_duel"
    },
    {
        "name": "Prince Lothric",
        "score": 5150,
        "theme": "lothric.mp3",
        "background": "Graphics/Backgrounds/boss_rush/LothricBG.png",
        "ability": "double_target"
    },
    {
        "name": "Nameless King",
        "score": 7500,
        "theme": "nameless_king.mp3",
        "background": "graphics/backgrounds/boss_rush/Namless_kingBG.png",
        "ability": "reduces_hand_size"
    },
    {
        "name": "Soul of Cinder",
        "score": 8500,
        "theme": "SoC.mp3",
        "background": "Graphics/Backgrounds/boss_rush/SoCBG.png",
        "ability": "phase_changes"
    },
    {
        "name": "Slave Knight Gael",
        "score": 10000,
        "theme": "Gael.mp3",
        "background": "Graphics/Backgrounds/boss_rush/GaelBG.png",
        "ability": "first_hand_penalty"
    }
]

class BossRushState(GameState):
    def __init__(self, nextState: str = "", playerInfo=None):
        self.restoring_from_save = False
        self.coming_from_run_info = False

        # Always check State.player_info first (like all states should)
        if hasattr(State, 'player_info') and State.player_info:
            playerInfo = State.player_info
        elif playerInfo:
            State.player_info = playerInfo
        else:
            return

        if hasattr(State, 'just_going_to_run_info') and State.just_going_to_run_info:
            self.coming_from_run_info = True
            State.just_going_to_run_info = False

        # Call parent init (GameState.__init__)
        super().__init__(nextState, playerInfo)

        # ===== SET State.player_info (don't be a dummy) =====
        State.player_info = self.playerInfo

        if (self.playerInfo and hasattr(self.playerInfo, 'saved_boss_rush_state') and  self.playerInfo.saved_boss_rush_state):
            self.restoring_from_save = True
            saved = self.playerInfo.saved_boss_rush_state

            # Restore game state
            self.hand = saved['hand']
            self.deck = saved['deck']
            self.used = saved['used']
            self.cardsSelectedList = saved['cardsSelectedList']
            self.playerJokers = saved['playerJokers']
            self.playerConsumables = saved['playerConsumables']
            self.hands_played_this_boss = saved['hands_played_this_boss']
            self.boss_phase = saved['boss_phase']
            self.last_hand_time = saved['last_hand_time']
            self.disabled_jokers = saved['disabled_jokers']
            self.playerInfo.roundScore = saved['roundScore']
            self.playerInfo.playerChips = saved['playerChips']
            self.playerInfo.playerMultiplier = saved['playerMultiplier']
            self.playerInfo.amountOfHands = saved['amountOfHands']
            self.playerInfo.amountOfDiscards = saved['amountOfDiscards']

            self.max_consumables = 5

            # Clear the saved state so we don't restore again
            self.playerInfo.saved_boss_rush_state = None

            # Update card display
            self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

        # ===== CHECK FOR RETURNING FROM SHOP =====
        if self.playerInfo and getattr(self.playerInfo, 'boss_rush_coming_from_shop', False):

            # Get saved data
            saved_jokers = getattr(self.playerInfo, 'saved_player_jokers', [])
            saved_consumables = getattr(self.playerInfo, 'saved_player_consumables', [])

            # Clear the flag
            self.playerInfo.boss_rush_coming_from_shop = False

            # Get boss index
            self.current_boss_index = getattr(self.playerInfo, 'boss_rush_current_index', 0)

            # ===== RESTORE JOKERS AND CONSUMABLES =====
            # Overwrite what parent GameState.__init__ set to []
            self.playerJokers = saved_jokers.copy()
            self.playerConsumables = saved_consumables.copy()

            # Restore boss rush data
            self.is_boss_rush = True
            self.bosses_defeated = getattr(self.playerInfo, 'boss_rush_bosses_defeated', 0)
            self.total_souls_earned = getattr(self.playerInfo, 'boss_rush_total_souls', 0)
            self.total_money = getattr(self.playerInfo, 'boss_rush_total_money', 0)
            self.total_jokers_used = getattr(self.playerInfo, 'boss_rush_total_jokers', 0)
            self.total_tarots_used = getattr(self.playerInfo, 'boss_rush_total_tarots', 0)

            # Initialize boss tracking
            self.boss_defeated_this_round = False
            self.debug_skip_requested = False
            self.current_boss_ability = None
            self.hands_played_this_boss = 0
            self.boss_phase = 1
            self.boss_ability_timer = pygame.time.get_ticks()
            self.last_hand_time = pygame.time.get_ticks()
            self.disabled_joker_this_round = False
            self.phase_changed = False
            self.disabled_jokers = []

            # Show transition
            self.show_post_shop_transition()
            return

        # ===== NORMAL INITIALIZATION =====
        self.is_boss_rush = True

        if self.restoring_from_save:
            # Restoring from X button save
            self.current_boss_index = getattr(self.playerInfo, 'boss_rush_current_index', 0)
            self.bosses_defeated = getattr(self.playerInfo, 'boss_rush_bosses_defeated', 0)
            self.total_souls_earned = getattr(self.playerInfo, 'boss_rush_total_souls', 0)
            self.total_money = getattr(self.playerInfo, 'boss_rush_total_money', 0)
            self.total_jokers_used = getattr(self.playerInfo, 'boss_rush_total_jokers', 0)
            self.total_tarots_used = getattr(self.playerInfo, 'boss_rush_total_tarots', 0)
        else:
            # Fresh start (including after losing)
            self.current_boss_index = 0
            self.bosses_defeated = 0
            self.total_souls_earned = 0
            self.total_money = 0
            self.total_jokers_used = 0
            self.total_tarots_used = 0

            if self.playerInfo:
                self.playerInfo.boss_rush_revive_used = False
                self.playerInfo.is_boss_rush = True

        # Initialize boss tracking
        self.boss_defeated_this_round = False
        self.debug_skip_requested = False
        self.current_boss_ability = None
        self.hands_played_this_boss = 0
        self.boss_phase = 1
        self.boss_ability_timer = pygame.time.get_ticks()
        self.last_hand_time = pygame.time.get_ticks()
        self.disabled_joker_this_round = False
        self.phase_changed = False
        self.disabled_jokers = []
        self.boss_rush_game_over = False

        if not self.restoring_from_save:
            self.initialize_boss_rush()  # This loads background and music
        else:
            if self.playerInfo:
                self.playerInfo.is_boss_rush = True
                self.current_boss_index = getattr(self.playerInfo, 'boss_rush_current_index', 0)
                self.bosses_defeated = getattr(self.playerInfo, 'boss_rush_bosses_defeated', 0)
                self.total_souls_earned = getattr(self.playerInfo, 'boss_rush_total_souls', 0)
                self.total_money = getattr(self.playerInfo, 'boss_rush_total_money', 0)
                self.total_jokers_used = getattr(self.playerInfo, 'boss_rush_total_jokers', 0)
                self.total_tarots_used = getattr(self.playerInfo, 'boss_rush_total_tarots', 0)

            # Load boss background (but don't restart music)
            boss = BOSS_RUSH_BOSSES[self.current_boss_index]
            self.current_boss_ability = boss["ability"]

            # Load boss background only
            bg_path = boss["background"]
            try:
                if os.path.exists(bg_path):
                    self.backgroundImage = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
                else:
                    self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
                    self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
            except Exception as e:
                self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
                self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))

            self.bossMusic_path = f"Graphics/Sounds/{boss['theme']}"

        if not self.coming_from_run_info:
            self.switchToBossTheme()

        self.restoring_from_save = False

    def initialize_boss_rush(self):
        """Initialize or reset boss rush game - loads new boss background, music, and resets game state"""
        if self.current_boss_index >= len(BOSS_RUSH_BOSSES):
            self.current_boss_index = 0

        boss = BOSS_RUSH_BOSSES[self.current_boss_index]
        self.current_boss_ability = boss["ability"]

        # Reset boss ability tracking
        self.hands_played_this_boss = 0
        self.boss_phase = 1
        self.boss_ability_timer = pygame.time.get_ticks()
        self.last_hand_time = pygame.time.get_ticks()
        self.disabled_joker_this_round = False
        self.phase_changed = False

        # Load boss background
        bg_path = boss["background"]
        try:
            if os.path.exists(bg_path):
                self.backgroundImage = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
            else:
                # Use default background if boss background not found
                self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
                self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        except Exception as e:
            # If any error occurs, use default background
            self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
            self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))

        # Create a SubLevel for this boss
        self.playerInfo.levelManager.curSubLevel = SubLevel(
            blind=Blind.BOSS,
            ante=1,
            bossLevel=boss["name"]
        )

        # Set the target score for this boss
        self.playerInfo.levelManager.curSubLevel.score = boss["score"]
        self.playerInfo.score = boss["score"]

        # Reset player state for new boss
        self.playerInfo.roundScore = 0
        self.playerInfo.playerChips = 0
        self.playerInfo.playerMultiplier = 0
        self.playerInfo.amountOfHands = 4
        self.playerInfo.amountOfDiscards = 4

        # Reset game state (new deck and hand)
        self.deck = self.deckManager.shuffleDeck(self.deckManager.createDeck(self.playerInfo.levelManager.curSubLevel))

        # Deal hand based on boss ability
        if self.current_boss_ability == "reduces_hand_size":
            # Nameless King: Start with only 6 cards instead of 8
            self.hand = self.deckManager.dealCards(self.deck, 6, self.playerInfo.levelManager.curSubLevel)
        else:
            self.hand = self.deckManager.dealCards(self.deck, 8, self.playerInfo.levelManager.curSubLevel)

        self.used = []
        self.cardsSelectedList = []
        self.cardsSelectedRect = {}
        self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

        # Load boss theme music
        self.bossMusic_path = f"Graphics/Sounds/{boss['theme']}"

        # Switch to boss theme music
        if not self.restoring_from_save or not self.coming_from_run_info:
            self.switchToBossTheme()

        # Reset play hand state
        self.playHandActive = False
        self.playHandStartTime = 0

    def update(self):
        if hasattr(self, 'show_simple_win') and self.show_simple_win:
            return

        if hasattr(self, 'boss_rush_game_over') and self.boss_rush_game_over:
            self.draw()
            return

        if self.debug_skip_requested:
            self.debug_skip_requested = False
            self.defeat_current_boss()
            return

        # Check if player has reached target score
        if self.playerInfo.roundScore >= self.playerInfo.levelManager.curSubLevel.score:
            if not self.boss_defeated_this_round:
                self.defeat_current_boss()
                return

        # Check for Soul of Cinder phase changes
        if self.current_boss_ability == "phase_changes":
            self.check_soul_of_cinder_phases()

        # Check for aggression timer (Gundyr and Soul of Cinder Phase 3)
        if self.current_boss_ability in ["aggression", "phase_changes"]:
            self.check_gundyr_aggression()

        self.isBossActive = True  # Tell parent we're already in boss mode
        self.bossMusicPlaying = True  # Tell parent music is already playing

        # ===== Also update boss abilities before parent update =====
        self.update_boss_abilities()

        # ===== Now call parent update for normal gameplay =====
        super().update()

        # ===== Make sure flags stay set =====
        self.isBossActive = True
        self.bossMusicPlaying = True

    def update_boss_abilities(self):
        """Update ongoing boss ability effects"""
        if not self.current_boss_ability:
            return

        # Artorias
        if (self.current_boss_ability == "disables_random_joker" and
                not self.disabled_joker_this_round):

            current_time = pygame.time.get_ticks()
            time_since_boss_start = current_time - self.boss_ability_timer

            if time_since_boss_start > 10000:  # 10 seconds
                self.disable_random_joker()
                self.disabled_joker_this_round = True
                print(f"ARTORIAS: 10 seconds passed - disabled a joker!")

        # Twin Princes - increasing score requirement
        if self.current_boss_ability == "double_target":
            current_target = self.playerInfo.levelManager.curSubLevel.score
            original_score = BOSS_RUSH_BOSSES[self.current_boss_index]["score"]
            doubled_score = original_score * 2

            # Check if player has 1 hand remaining
            if self.playerInfo.amountOfHands == 1 and current_target != doubled_score:
                # DOUBLE THE TARGET!
                self.playerInfo.levelManager.curSubLevel.score = doubled_score
                self.playerInfo.score = doubled_score

                # Show visual effect
                self.show_double_target_effect()

    def check_gundyr_aggression(self):
        """Check if player is taking too long for Gundyr or Soul of Cinder Phase 3"""
        current_time = pygame.time.get_ticks()
        time_since_last_hand = current_time - self.last_hand_time

        # Gundyr's time pressure: 15 seconds
        if self.current_boss_ability == "aggression" and time_since_last_hand > 15000:
            # Make sure we have cards to discard
            if self.hand and len(self.hand) > 0:
                try:
                    card = random.choice(self.hand)
                    self.hand.remove(card)
                    self.deck.append(card)

                    if len(self.hand) == 0 and not self.gameOverTriggered:
                        self.trigger_card_depletion_game_over()
                        return

                    self.updateCards(400, 520, self.cards, self.hand, scale=1.2)

                except (ValueError, IndexError) as e:
                    print(f"Gundyr discard error: {e}")
            self.last_hand_time = current_time

        # Soul of Cinder Phase 3 time pressure: 10 seconds
        elif (self.current_boss_ability == "phase_changes" and
              self.boss_phase == 3 and
              time_since_last_hand > 10000):
            if self.hand and len(self.hand) > 0:
                try:
                    card = random.choice(self.hand)
                    self.hand.remove(card)
                    self.deck.append(card)
                    if len(self.hand) == 0 and not self.gameOverTriggered:
                        self.trigger_card_depletion_game_over()
                        return
                    self.updateCards(400, 520, self.cards, self.hand, scale=1.2)
                except (ValueError, IndexError) as e:
                    print(f"Soul of Cinder Phase 3 discard error: {e}")
            self.last_hand_time = current_time

    def playHand(self):
        # Track hands played for this boss
        self.hands_played_this_boss += 1

        # Apply pre-hand abilities
        self.apply_pre_hand_abilities()

        # Soul of Cinder Phase 4: Random discard from selected cards
        if (self.current_boss_ability == "phase_changes" and
                self.boss_phase == 4 and
                self.cardsSelectedList):

            # 50% chance to trigger discard
            if random.random() < 0.5:
                try:
                    # Choose a random card from selected cards
                    card = random.choice(self.cardsSelectedList)

                    # Double-check card is still in selected list
                    if card not in self.cardsSelectedList:
                        return

                    # Remove from selected list
                    self.cardsSelectedList.remove(card)

                    # Deselect it visually if it's still in the cards dictionary
                    if card in self.cards:
                        card.isSelected = False
                        self.cards[card].y += 50

                    # Handle as destroyed card
                    result = {"destroyed_cards": [card], "effect": "soul_of_cinder_discard"}
                    super().handleDestroyedCards(result)

                    if hasattr(self, 'destroy_sound'):
                        self.destroy_sound.play()

                    # Don't play hand if no cards left after discard
                    if not self.cardsSelectedList:
                        return

                except (ValueError, IndexError, KeyError) as e:
                    # Card was already removed or doesn't exist anymore
                    print(f"Soul of Cinder Phase 4 discard error: {e}")

        # Call parent's playHand
        super().playHand()

        # Apply post-hand abilities
        self.apply_post_hand_abilities()

        # Check for Soul of Cinder phase changes after scoring
        if self.current_boss_ability == "phase_changes":
            self.check_soul_of_cinder_phases()

        # Update last hand time for time pressure mechanics
        self.last_hand_time = pygame.time.get_ticks()

    def apply_pre_hand_abilities(self):
        """Apply abilities that affect the hand before playing"""
        if not self.current_boss_ability:
            return

        # Sir Alonne - Honorable Duel (max 4 cards per hand)
        if self.current_boss_ability == "honorable_duel":
            if len(self.cardsSelectedList) > 4:
                # Trim selection to max 4 cards
                self.cardsSelectedList = self.cardsSelectedList[:4]
                # Also update visual selection
                self.cardsSelectedRect = {k: v for k, v in list(self.cardsSelectedRect.items())[:4]}

    def apply_post_hand_abilities(self):
        if not self.current_boss_ability:
            return

        # Restore Gael's chips/multiplier after scoring
        if self.current_boss_ability == "first_hand_penalty":
            if self.hands_played_this_boss:
                if hasattr(self, 'original_chips'):
                    self.playerInfo.playerChips = self.original_chips
                    del self.original_chips
                if hasattr(self, 'original_mult'):
                    self.playerInfo.playerMultiplier = self.original_mult
                    del self.original_mult

                # Show penalty text
                penalty_text = f"(GAEL PENALTY -50%) -> +{self.pending_round_add}"
                self.scoreBreakdownTextSurface = self.playerInfo.textFont2.render(
                    penalty_text, True, (255, 100, 100)
                )

        # Restore Soul of Cinder's multiplier
        if self.current_boss_ability == "phase_changes" and self.boss_phase == 3:
            if hasattr(self, 'original_mult_soc'):
                self.playerInfo.playerMultiplier = self.original_mult_soc
                del self.original_mult_soc

            # Show penalty text
            penalty_text = f"(SOUL OF CINDER -5%) -> +{self.pending_round_add}"
            self.scoreBreakdownTextSurface = self.playerInfo.textFont2.render(
                penalty_text, True, (255, 100, 100)
            )
    def check_soul_of_cinder_phases(self):
        if self.current_boss_ability != "phase_changes":
            return

        target_score = self.playerInfo.levelManager.curSubLevel.score
        if target_score <= 0:
            return

        current_progress = self.playerInfo.roundScore / target_score

        # Phase 1 → Phase 2 at 25% progress
        if self.boss_phase == 1 and current_progress >= 0.25:
            self.boss_phase = 2
            self.phase_changed = True
            # Phase 2: Disable random joker
            self.disable_random_joker()

        # Phase 2 → Phase 3 at 50% progress
        elif self.boss_phase == 2 and current_progress >= 0.5:
            self.boss_phase = 3
            self.phase_changed = True
            # Phase 3: Time pressure + -5% score reduction
            self.last_hand_time = pygame.time.get_ticks()

        # Phase 4 at 75% progress
        elif self.boss_phase == 3 and current_progress >= 0.75:
            self.boss_phase = 4
            self.phase_changed = True
            # Phase 4: Random card discard

    def defeat_current_boss(self):
        """Handle boss defeat and show transition to next boss"""
        self.boss_defeated_this_round = True
        shop_money = 100

        # Awards for defeating this boss
        souls_earned = 5 + (self.current_boss_index * 2)
        self.playerInfo.souls += souls_earned
        self.total_souls_earned += souls_earned
        self.playerInfo.playerMoney += shop_money
        self.bosses_defeated += 1

        # Fade out music for transition
        pygame.mixer.music.fadeout(500)

        # Move to next boss
        self.current_boss_index += 1

        if self.current_boss_index < len(BOSS_RUSH_BOSSES):
            # === GO TO SHOP ===
            self.go_to_shop_between_bosses()
        else:
            # All bosses defeated!
            self.win_transition()

    def go_to_shop_between_bosses(self):
        # ===== SAVE TO State.player_info (CONSISTENT WITH GameState) =====
        State.screenshot = self.screen.copy()
        State.player_info = self.playerInfo  # CONSISTENT!

        # ===== SAVE BOSS RUSH DATA TO playerInfo =====
        self.playerInfo.is_boss_rush = True
        self.playerInfo.boss_rush_current_index = self.current_boss_index
        self.playerInfo.boss_rush_bosses_defeated = self.bosses_defeated
        self.playerInfo.boss_rush_total_souls = self.total_souls_earned
        self.playerInfo.boss_rush_total_money = self.total_money
        self.playerInfo.boss_rush_total_jokers = self.total_jokers_used
        self.playerInfo.boss_rush_total_tarots = self.total_tarots_used


        self.playerInfo.boss_rush_coming_from_shop = True

        # Switch theme
        super().switchToNormalTheme(force=True)

        # Transition
        self.isFinished = True
        self.nextState = "ShopState"

    def show_post_shop_transition(self):
        """Show boss info card after returning from shop (screen should already be black)"""
        next_boss = BOSS_RUSH_BOSSES[self.current_boss_index]

        # Show boss info card on BLACK screen
        card_width, card_height = 500, 300
        card_x, card_y = 650 - card_width // 2, 375 - card_height // 2

        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (30, 30, 50), card_surface.get_rect(), border_radius=15)
        pygame.draw.rect(card_surface, (60, 60, 80), card_surface.get_rect(), 3, border_radius=15)

        title_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 40)
        title_text = title_font.render("NEXT BOSS", True, (255, 215, 0))
        card_surface.blit(title_text, (card_width // 2 - title_text.get_width() // 2, 30))

        name_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 50)
        name_text = name_font.render(next_boss["name"], True, (255, 100, 100))
        card_surface.blit(name_text, (card_width // 2 - name_text.get_width() // 2, 100))

        score_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 35)
        score_text = score_font.render(f"Score: {next_boss['score']}", True, (200, 200, 255))
        card_surface.blit(score_text, (card_width // 2 - score_text.get_width() // 2, 180))

        # Money notification
        money_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 28)
        money_text = money_font.render(f"+$100 earned", True, (100, 255, 100))
        card_surface.blit(money_text, (card_width // 2 - money_text.get_width() // 2, 230))

        progress_text = score_font.render(
            f"{self.current_boss_index + 1}/{len(BOSS_RUSH_BOSSES)}",
            True, (200, 255, 200)
        )
        card_surface.blit(progress_text, (card_width // 2 - progress_text.get_width() // 2, 270))

        self.screen.fill((0, 0, 0))  # Black background
        self.screen.blit(card_surface, (card_x, card_y))

        continue_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 25)
        continue_text = continue_font.render("Continuing in 2 seconds...", True, (150, 150, 150))
        self.screen.blit(continue_text, (650 - continue_text.get_width() // 2, 700))

        if hasattr(self, 'tvOverlay'):
            self.screen.blit(self.tvOverlay, (0, 0))

        pygame.display.update()

        # Wait for card to show
        pygame.time.wait(2000)

        # --- FADE OUT the transition card to black ---
        for alpha in [255, 180, 100, 0]:  # Card fades OUT to black
            self.screen.fill((0, 0, 0))  # Black background

            # Draw card with decreasing alpha (fading out)
            card_surface.set_alpha(alpha)
            self.screen.blit(card_surface, (card_x, card_y))

            # Fade continue text too
            continue_text_surface = continue_font.render("Continuing in 2 seconds...", True,
                                                         (150, 150, 150, alpha))
            self.screen.blit(continue_text_surface, (650 - continue_text.get_width() // 2, 700))

            if hasattr(self, 'tvOverlay'):
                self.screen.blit(self.tvOverlay, (0, 0))

            pygame.display.update()
            pygame.time.wait(100)

        # Screen is now BLACK again

        # --- Initialize the next boss ---
        self.boss_defeated_this_round = False
        self.initialize_boss_rush()  # This loads background, plays music, resets game

        # --- FADE IN from black to new boss ---
        fade_surface = pygame.Surface((1300, 750), pygame.SRCALPHA)
        for alpha in [255, 180, 100, 0]:  # Black fades OUT, revealing scene underneath
            # Draw the new scene
            self.screen.blit(self.background, (0, 0))
            super().draw()

            # Apply black overlay with decreasing alpha
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(fade_surface, (0, 0))

            if hasattr(self, 'tvOverlay'):
                self.screen.blit(self.tvOverlay, (0, 0))

            pygame.display.update()
            pygame.time.wait(100)

    def win_screen(self):
        try:
            pygame.mixer.music.stop()
            victory_music_path = "graphics/Sounds/nameless_song.mp3"
            if os.path.exists(victory_music_path):
                pygame.mixer.music.load(victory_music_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.7)
            else:
                print(f"Nameless song not found: {victory_music_path}")
        except Exception as e:
            print(f"Error playing Nameless song: {e}")

        # Clear screen to black
        self.screen.fill((0, 0, 0))

        # Draw title
        title_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 72)
        title = title_font.render("BOSS RUSH COMPLETE!", True, (255, 215, 0))
        self.screen.blit(title, (650 - title.get_width() // 2, 100))


        stats_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 48)

        congrats = stats_font.render(f"Thank you for playing Boss Rush! (This was a bitch to make...)",
                                     True,
                                     (100, 255, 100))
        ps = stats_font.render(f"I ' M  I N  Y O U R  W A L L S, - Revel",
                               True,
                               (136, 8, 8))
        self.screen.blit(congrats, (650 - congrats.get_width() // 2, 250))
        self.screen.blit(ps, (950 - congrats.get_width() // 2, 200))

        souls_text = stats_font.render(f"Souls Earned: {self.total_souls_earned}", True, (255, 215, 0))
        self.screen.blit(souls_text, (650 - souls_text.get_width() // 2, 320))

        self.screen.blit(self.tvOverlay, (0, 0))
        pygame.display.update()

        start_time = pygame.time.get_ticks()
        show_L_prompt = False

        waiting = True
        while waiting:
            current_time = pygame.time.get_ticks()

            if not show_L_prompt and (current_time - start_time) > 1000:
                show_L_prompt = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        break

                    if event.key == pygame.K_l and show_L_prompt:
                        pygame.mixer.music.fadeout(500)

                        self.play_video_fullscreen()

                        self.return_to_main_menu()
                        return

            self.screen.fill((0, 0, 0), (0, 550, 1300, 200))

            prompt_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 32)
            blink_on = (current_time // 600) % 2 == 0

            if blink_on:
                space_prompt = prompt_font.render("Press SPACE to return to Main Menu", True, (200, 200, 255))
                self.screen.blit(space_prompt, (650 - space_prompt.get_width() // 2, 600))

            if show_L_prompt and blink_on:
                L_prompt = prompt_font.render("Press L for ???", True, (255, 100, 100))
                self.screen.blit(L_prompt, (650 - L_prompt.get_width() // 2, 650))

            overlay_portion = pygame.Surface((1300, 200), pygame.SRCALPHA)
            overlay_portion.blit(self.tvOverlay, (0, 0), (0, 550, 1300, 200))
            self.screen.blit(overlay_portion, (0, 550))

            pygame.display.update()
            pygame.time.wait(50)

        self.return_to_main_menu()

    def play_video_fullscreen(self):
        try:
            import cv2
            import numpy as np

            video_path = "graphics/secret/Venom.mp4"
            audio_path = "graphics/secret/Venom_audio.mp3"

            if not os.path.exists(video_path):
                print(f"Video not found: {video_path}")
                return False

            if os.path.exists(audio_path):
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()

            cap = cv2.VideoCapture(video_path)

            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30

            clock = pygame.time.Clock()
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pass

                frame_count += 1

                # Convert and process frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (1300, 750))
                frame = np.rot90(frame)
                frame_surface = pygame.surfarray.make_surface(frame)

                self.screen.blit(frame_surface, (0, 0))
                pygame.display.flip()


                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        pygame.mixer.music.stop()
                        return True

                clock.tick(fps)

            cap.release()
            pygame.mixer.music.stop()
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def show_video_fallback(self):
        self.screen.fill((0, 0, 0))

        font = pygame.font.Font('Graphics/Text/m6x11.ttf', 40)
        text1 = font.render("Kept you waiting huh...", True, (255, 215, 0))
        text2 = font.render("(Video playback unavailable)", True, (200, 200, 200))

        self.screen.blit(text1, (650 - text1.get_width() // 2, 300))
        self.screen.blit(text2, (650 - text2.get_width() // 2, 360))

        pygame.display.update()
        pygame.time.wait(2000)

    def return_to_main_menu(self):
        # Switch to normal theme
        super().switchToNormalTheme(force=True)

        # Set state to finished
        self.isFinished = True
        self.nextState = "StartState"

        # Reset player's boss rush flag
        if self.playerInfo:

            self.playerInfo.is_boss_rush = False

            # Reset all player resources
            self.playerInfo.souls = 0
            self.playerInfo.playerMoney = 0
            self.playerInfo.heat = 0

            # Reset run-specific stats
            self.playerInfo.roundScore = 0
            self.playerInfo.playerChips = 0
            self.playerInfo.playerMultiplier = 0

            # Clear all collections
            self.playerInfo.jokers = []
            self.playerInfo.tarots = []
            self.playerInfo.consumables = []

            attrs_to_clear = [
                'is_boss_rush',
                'boss_rush_current_index',
                'boss_rush_bosses_defeated',
                'boss_rush_total_souls',
                'boss_rush_total_money',
                'boss_rush_total_jokers',
                'boss_rush_total_tarots',
                'boss_rush_coming_from_shop',
                'saved_player_jokers',
                'saved_player_consumables',
                'saved_boss_rush_state',
                'boss_rush_revive_used',
            ]

            for attr in attrs_to_clear:
                if hasattr(self.playerInfo, attr):
                    delattr(self.playerInfo, attr)

    def draw(self):
        if self.showReviveOption or self.gameOverTriggered:
            super().draw()
            return

        # Normal gameplay drawing
        self.screen.blit(self.background, (0, 0))
        super().draw()

    def win_transition(self):
        boss_scene = self.screen.copy()

        fade = pygame.Surface((1300, 750), pygame.SRCALPHA)

        for alpha in [64, 128, 192, 255]:
            self.screen.blit(boss_scene, (0, 0))
            fade.fill((0, 0, 0, alpha))
            self.screen.blit(fade, (0, 0))

            if hasattr(self, 'tvOverlay'):
                self.screen.blit(self.tvOverlay, (0, 0))

            pygame.display.update()
            pygame.time.wait(50)

        self.win_screen()

    def userInput(self, events):
        # Handle win screen input
        if events.type == pygame.QUIT:

            self.save_boss_rush_progress()

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)

            self.isFinished = True
            super().switchToNormalTheme(force=True)
            self.nextState = "StartState"
            return

        if events.type == pygame.MOUSEBUTTONDOWN:
            mousePos = pygame.mouse.get_pos()

            # Check if run info button is clicked
            if self.playerInfo.runInfoRect.collidepoint(
                    (mousePos[0] - self.playerInfo.playerInfo2.x,
                     mousePos[1] - self.playerInfo.playerInfo2.y)):
                State.screenshot = self.screen.copy()
                self.isFinished = True
                State.just_going_to_run_info = True
                self.nextState = "RunInfoState"

                self.save_boss_rush_progress()

                return

        if hasattr(self, 'show_simple_win') and self.show_simple_win:
                if isinstance(events, pygame.event.Event):
                    events_list = [events]
                else:
                    events_list = events

                for event in events_list:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.win_screen()

                        return

                return

        # Call parent for normal gameplay input
        super().userInput(events)

    def switchToBossTheme(self):
        try:
            # First stop any currently playing music
            pygame.mixer.music.stop()

            # Load and play the boss theme
            pygame.mixer.music.load(self.bossMusic_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.7)
        except Exception as e:
            super().switchToNormalTheme()

    def userInputCards(self, events):
        """Override card selection to enforce Honorable Duel"""
        if events.type == pygame.MOUSEBUTTONDOWN and not self.playHandActive:
            mousePos = pygame.mouse.get_pos()

            # Iterate in reverse to select the top-most card first
            for card in reversed(list(self.cards.keys())):
                if self.cards[card].collidepoint(mousePos):
                    if not card.isSelected:
                        if len(self.cardsSelectedList) >= 5:
                            # Normal limit: Cannot select more than 5 cards
                            return

                        # Sir Alonne's Honorable Duel: Max 4 cards per hand
                        if self.current_boss_ability == "honorable_duel" and len(self.cardsSelectedList) >= 4:
                            return

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

    def show_double_target_effect(self):
        """Show visual effect when target is doubled"""
        # Flash red warning
        for _ in range(3):
            flash = pygame.Surface((1300, 750), pygame.SRCALPHA)
            flash.fill((255, 50, 50, 100))
            self.screen.blit(flash, (0, 0))
            pygame.display.update()
            pygame.time.wait(100)

            self.draw()
            pygame.display.update()
            pygame.time.wait(100)

        # Show warning text
        warning_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 40)
        warning_text = warning_font.render("TARGET DOUBLED!", True, (255, 50, 50))
        text_rect = warning_text.get_rect(center=(650, 200))

        # Draw with background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 200), bg_surface.get_rect(), border_radius=8)

        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(warning_text, text_rect)
        pygame.display.update()
        pygame.time.wait(1500)

    def disable_random_joker(self):
        """Disable a random joker - used by Artorias and Soul of Cinder Phase 2"""
        try:
            # Check if player has jokers in GameState
            if hasattr(self, 'playerJokers') and self.playerJokers:
                # Since playerJokers stores names, we need to find the actual joker objects
                available_jokers = []

                # First, find all joker objects that match the player's joker names
                for joker_name in self.playerJokers:
                    # Find the joker object in jokerDeck
                    for joker_obj in self.jokerDeck:
                        if joker_obj.name == joker_name:
                            available_jokers.append(joker_obj)
                            break

                if available_jokers:
                    # Choose a random joker to disable
                    joker_to_disable = random.choice(available_jokers)

                    # === SIMPLE FIX: Just add to disabled_jokers list ===
                    # This joker will still show in display but won't activate
                    if joker_to_disable.name not in self.disabled_jokers:
                        self.disabled_jokers.append(joker_to_disable.name)
                        print(f"DISABLED: {joker_to_disable.name} added to disabled_jokers")

                    # Different message based on which boss is doing it
                    boss = BOSS_RUSH_BOSSES[self.current_boss_index]["name"]
                    if boss == "Artorias":
                        print(f"ARTORIAS: Disabled joker: {joker_to_disable.name}!")
                        # Show visual effect
                        self.show_joker_disabled_effect(joker_to_disable.name, "Artorias")
                    elif boss == "Soul of Cinder" and self.boss_phase == 2:
                        print(f"SOUL OF CINDER PHASE 2: Disabled joker: {joker_to_disable.name}!")
                        # Show visual effect
                        self.show_joker_disabled_effect(joker_to_disable.name, "Soul of Cinder")
                else:
                    # No joker objects found
                    boss = BOSS_RUSH_BOSSES[self.current_boss_index]["name"]
                    if boss == "Artorias":
                        print("ARTORIAS: Could not find joker objects!")
                    elif boss == "Soul of Cinder" and self.boss_phase == 2:
                        print("SOUL OF CINDER PHASE 2: Could not find joker objects!")
            else:
                # Player has no jokers at all
                boss = BOSS_RUSH_BOSSES[self.current_boss_index]["name"]
                if boss == "Artorias":
                    print("ARTORIAS: You have no jokers!")
                elif boss == "Soul of Cinder" and self.boss_phase == 2:
                    print("SOUL OF CINDER PHASE 2: You have no jokers!")
        except Exception as e:
            # Catch any error
            print(f"Disable joker error: {e}")
            import traceback
            traceback.print_exc()

    def show_joker_disabled_effect(self, joker_name, boss_name):
        """Show visual effect when a joker is disabled by a boss"""
        # Different colors based on which boss is disabling
        if boss_name == "Artorias":
            color = (100, 150, 255)  # Blue for Artorias
            boss_title = "ARTORIAS"
        else:  # Soul of Cinder
            color = (255, 150, 50)  # Orange for Soul of Cinder
            boss_title = "SOUL OF CINDER"

        # Create a semi-transparent overlay
        overlay = pygame.Surface((1300, 750), pygame.SRCALPHA)
        overlay.fill((*color, 50))  # Semi-transparent color

        # Show the overlay for a brief moment
        self.screen.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.wait(100)

        # Clear the overlay
        self.draw()  # Redraw the normal game screen
        pygame.display.update()
        pygame.time.wait(100)

        # Show again for another flash
        self.screen.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.wait(100)

        # Create the notification message
        notification_font = pygame.font.Font('Graphics/Text/m6x11.ttf', 36)
        message = f"{boss_title}: DISABLED {joker_name.upper()}"
        notification_text = notification_font.render(message, True, color)

        # Position the notification at the top center
        text_rect = notification_text.get_rect(center=(650, 50))

        # Create a background for the text
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 200), bg_surface.get_rect(), border_radius=8)

        # Draw everything
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(notification_text, text_rect)

        pygame.display.update()

        # Show the notification for 2 seconds
        pygame.time.wait(2000)

        # Redraw the normal screen
        self.draw()
        pygame.display.update()

        try:
            disable_sound = pygame.mixer.Sound('Graphics/Sounds/thunder.wav')
            disable_sound.play()
        except:
            pass

    def trigger_card_depletion_game_over(self):
        self.showReviveOption = True
        self.gameOverTriggered = True
        self.showRedTint = True
        self.boss_rush_game_over = True

        pygame.mixer.music.stop()

        if hasattr(self, 'gameOverSound'):
            self.gameOverSound.play()


    def discardCards(self, removeFromHand: bool):
        """Override to check for empty deck before trying to draw"""
        # Check if we need to draw cards but deck is empty
        if len(self.hand) < 8 and len(self.deck) == 0:
            self.trigger_card_depletion_game_over()
            return

        # Call parent implementation
        super().discardCards(removeFromHand)

    def save_boss_rush_progress(self):
        # Added this for better saving
        if not self.playerInfo:
            return

        print("💾 SAVING boss rush progress...")

        # Save boss rush tracking
        self.playerInfo.is_boss_rush = True
        self.playerInfo.boss_rush_current_index = self.current_boss_index
        self.playerInfo.boss_rush_bosses_defeated = self.bosses_defeated
        self.playerInfo.boss_rush_total_souls = self.total_souls_earned
        self.playerInfo.boss_rush_total_money = self.total_money
        self.playerInfo.boss_rush_total_jokers = self.total_jokers_used
        self.playerInfo.boss_rush_total_tarots = self.total_tarots_used

        # Save current jokers and consumables
        self.playerInfo.saved_player_jokers = self.playerJokers.copy() if hasattr(self, 'playerJokers') else []
        self.playerInfo.saved_player_consumables = self.playerConsumables.copy() if hasattr(self,'playerConsumables') else []

        self.playerInfo.saved_boss_rush_state = {
            'hand': self.hand.copy() if hasattr(self, 'hand') else [],
            'deck': self.deck.copy() if hasattr(self, 'deck') else [],
            'used': self.used.copy() if hasattr(self, 'used') else [],
            'cardsSelectedList': self.cardsSelectedList.copy() if hasattr(self, 'cardsSelectedList') else [],
            'playerJokers': self.playerJokers.copy() if hasattr(self, 'playerJokers') else [],
            'playerConsumables': self.playerConsumables.copy() if hasattr(self, 'playerConsumables') else [],
            'hands_played_this_boss': self.hands_played_this_boss if hasattr(self, 'hands_played_this_boss') else 0,
            'boss_phase': self.boss_phase if hasattr(self, 'boss_phase') else 1,
            'last_hand_time': self.last_hand_time if hasattr(self, 'last_hand_time') else pygame.time.get_ticks(),
            'disabled_jokers': self.disabled_jokers.copy() if hasattr(self, 'disabled_jokers') else [],
            'roundScore': self.playerInfo.roundScore,
            'playerChips': self.playerInfo.playerChips,
            'playerMultiplier': self.playerInfo.playerMultiplier,
            'amountOfHands': self.playerInfo.amountOfHands,
            'amountOfDiscards': self.playerInfo.amountOfDiscards
        }
