import pygame
from States.Core.StateClass import State
import math

class StartState(State):
    def __init__(self, nextState: str = ""):
        super().__init__(nextState)
        # ----------------------------- Background --------------------------------
        self.backgroundImage = pygame.image.load('Graphics/Backgrounds/introBackground.jpeg')
        self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        self.backgroundRect = self.background.get_rect(topleft=(0, 0))

        # ----------------------------- Title -------------------------------------
        self.titleImage = pygame.image.load('Graphics/Backgrounds/balatroTitle.png')
        original_width, original_height = self.titleImage.get_size()
        scale_factor = 700 / original_width
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        self.baseTitleSize = (new_width, new_height)
        self.title = pygame.transform.scale(self.titleImage, self.baseTitleSize)
        self.titleRect = self.title.get_rect(midtop=(650, 30))

        # Breathing animation variables for title
        self.breathAmplitude = 10  # pixels (not directly used, just for reference)
        self.breathSpeed = 0.005   # smaller = slower breathing
        self.breathTime = 0

        # ----------------------------- Text --------------------------------------
        self.textFont1 = pygame.font.Font('Graphics/Text/m6x11.ttf', 50)
        self.textFont2 = pygame.font.Font('Graphics/Text/m6x11.ttf', 40)
        self.textPlay = self.textFont1.render("PLAY", True, 'white')
        self.textInstructions = self.textFont2.render("HELP", True, 'white')
        self.textQuit = self.textFont1.render("QUIT", True, 'white')
        self.textBossRush = self.textFont1.render("BOSS RUSH", True, 'white')

        # ----------------------------- Title Card --------------------------------
        self.titleCardImage = pygame.image.load('Graphics/Backgrounds/titleCard.png')
        self.baseCardSize = (150, 220)
        self.titleCard = pygame.transform.scale(self.titleCardImage, self.baseCardSize)
        self.titleCardRect = self.titleCard.get_rect(topleft=(575, 150))
        self.mouseDragging = False
        self.isMouseInCard = False

        # ----------------------------- button Bar --------------------------------
        self.buttonBar = pygame.Rect(self.titleRect.x, 540, 690, 120)
        self.buttonBarSurface = pygame.Surface((690, 120), pygame.SRCALPHA)

        # Boss rush button
        self.buttonBossRush = pygame.Rect(0, 0, 200, 75)

        # Buttons
        self.buttonPlay = pygame.Rect(0, 0, 160, 75)
        self.buttonInstructions = pygame.Rect(0, 0, 150, 50)
        self.buttonQuit = pygame.Rect(0, 0, 160, 75)

        total_width = self.buttonPlay.width + self.buttonInstructions.width + self.buttonBossRush.width + self.buttonQuit.width
        spacing = (self.buttonBar.width - total_width) // 5  # even spacing

        x = spacing
        self.buttonPlay.topleft = (x, (self.buttonBar.height - self.buttonPlay.height) // 2)
        x += self.buttonPlay.width + spacing
        # Boss rush button
        self.buttonBossRush.topleft = (x, (self.buttonBar.height - self.buttonBossRush.height) // 2)
        x += self.buttonBossRush.width + spacing

        self.buttonInstructions.topleft = (x, (self.buttonBar.height - self.buttonInstructions.height) // 2)
        x += self.buttonInstructions.width + spacing
        self.buttonQuit.topleft = (x, (self.buttonBar.height - self.buttonQuit.height) // 2)

        # ----------------------------- TV Overlay --------------------------------
        self.tvOverlay = pygame.image.load('Graphics/Backgrounds/CRT.png').convert_alpha()
        self.tvOverlay = pygame.transform.scale(self.tvOverlay, (1300, 750))

        # ----------------------------- Help Screen --------------------------------
        self.showHelpScreen = False
        self.helpFont = pygame.font.Font('Graphics/Text/m6x11.ttf', 30)
        self.helpText = [
            "Welcome to Balatro!",
            "Goal: Play the best hand and win the game.",
            "1. Select up to 5 Cards by clicking on them.",
            "2. Play your hand with the 'PLAY' button.",
            "3. Sort your hand using 'Rank' or 'Suit'.",
            "4. Discard unwanted Cards with the 'QUIT' button.",
            "5. Have fun and enjoy the game!",
            "",
            "BOSS RUSH MODE:",
            "Face 7 Dark Souls bosses back-to-back!",
            "- Each boss has unique music and background",
            "- Beat all bosses to win!",
            "- Earn extra souls for each boss defeated"
        ]

    # ----------------------------- Update ------------------------------------
    def update(self):
        self.breathTime += self.breathSpeed  # increment small delta each frame
        self.updateBreathTitle()
        self.draw()

    # ----------------------------- Draw --------------------------------------
    def draw(self):
        State.screen.blit(self.background, self.backgroundRect)
        State.screen.blit(self.title, self.titleRect)
        State.screen.blit(self.titleCard, self.titleCardRect)

        pygame.draw.rect(State.screen, (50, 50, 50), self.buttonBar)
        self.buttonBarSurface.fill((0, 0, 0, 0))
        self.drawbuttons()
        State.screen.blit(self.buttonBarSurface, self.buttonBar)

        # Draw CRT overlay on top
        State.screen.blit(self.tvOverlay, (0, 0))

        # Draw Help Screen Overlay if active
        if self.showHelpScreen:
            self.drawHelpScreen()

    # ----------------------------- Help Screen --------------------------------
    def drawHelpScreen(self):
        overlay = pygame.Surface((1300, 750), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # semi-transparent dark overlay
        State.screen.blit(overlay, (0, 0))

        # Better formatting
        wrapped_lines = []
        max_chars_per_line = 60

        for line in self.helpText:
            if len(line) <= max_chars_per_line:
                wrapped_lines.append(line)
            else:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_chars_per_line:
                        if current_line:
                            current_line += " " + word
                        else:
                            current_line = word
                    else:
                        wrapped_lines.append(current_line)
                        current_line = word
                if current_line:
                    wrapped_lines.append(current_line)

        start_y = 100
        line_height = 40

        for i, line in enumerate(wrapped_lines):
            text_surf = self.helpFont.render(line, True, 'white')
            text_rect = text_surf.get_rect(center=(650, start_y + i * line_height))
            State.screen.blit(text_surf, text_rect)

        closeText = self.helpFont.render("Click anywhere to close", True, 'yellow')
        closeRect = closeText.get_rect(center=(650, 700))
        State.screen.blit(closeText, closeRect)

    # ----------------------------- Draw Buttons --------------------------------
    def drawbuttons(self):
        mousePos = pygame.mouse.get_pos()
        mousePosbuttonBar = (mousePos[0] - self.buttonBar.x, mousePos[1] - self.buttonBar.y)

        def draw_button(rect, base_color, hover_color, text_surface):
            is_hover = rect.collidepoint(mousePosbuttonBar)
            color = hover_color if is_hover else base_color
            pygame.draw.rect(self.buttonBarSurface, color, rect, border_radius=20)
            text_rect = text_surface.get_rect(center=rect.center)
            self.buttonBarSurface.blit(text_surface, text_rect)

        play_base, play_hover = (30, 144, 255), (0, 191, 255)
        instruct_base, instruct_hover = (255, 140, 0), (255, 165, 0)
        quit_base, quit_hover = (178, 34, 34), (255, 69, 58)
        # Boss rush stuff
        boss_rush_base, boss_rush_hover = (178, 34, 34), (255, 69, 0)  # Red/Orange for boss rush

        draw_button(self.buttonPlay, play_base, play_hover, self.textPlay)
        draw_button(self.buttonBossRush, boss_rush_base, boss_rush_hover, self.textBossRush)
        draw_button(self.buttonInstructions, instruct_base, instruct_hover, self.textInstructions)
        draw_button(self.buttonQuit, quit_base, quit_hover, self.textQuit)

    # ----------------------------- Breathing Animation for Title ------------------------
    def updateBreathTitle(self):
        scale = 1 + math.sin(self.breathTime) * 0.05  # 5% scaling
        newWidth = int(self.baseTitleSize[0] * scale)
        newHeight = int(self.baseTitleSize[1] * scale)
        self.title = pygame.transform.scale(self.titleImage, (newWidth, newHeight))
        self.titleRect = self.title.get_rect(midtop=self.titleRect.midtop)

    # ----------------------------- User Input --------------------------------
    def userInput(self, events):
        mousePos = pygame.mouse.get_pos()
        mousePosbuttonBar = (mousePos[0] - self.buttonBar.x, mousePos[1] - self.buttonBar.y)
        self.isMouseInCard = self.titleCardRect.collidepoint(mousePos)

        if events.type == pygame.QUIT:
            self.isFinished = True
        if events.type == pygame.KEYDOWN and events.key == pygame.K_ESCAPE:
            self.isFinished = True

        # Mouse events
        if events.type == pygame.MOUSEBUTTONDOWN:
            if self.showHelpScreen:
                self.showHelpScreen = False  # close help overlay on click
            elif self.isMouseInCard:
                self.mouseDragging = True
            elif self.buttonQuit.collidepoint(mousePosbuttonBar):
                self.buttonSound.play()
                self.isFinished = True
                self.nextState = "EXIT"
            elif self.buttonPlay.collidepoint(mousePosbuttonBar):
                self.buttonSound.play()
                self.isFinished = True
                self.nextState = "GameState"
            elif self.buttonInstructions.collidepoint(mousePosbuttonBar):
                self.buttonSound.play()
                self.showHelpScreen = True  # show help overlay
            elif self.buttonBossRush.collidepoint(mousePosbuttonBar):  # NEW
                self.buttonSound.play()
                self.isFinished = True
                self.nextState = "BossRushState"

        elif events.type == pygame.MOUSEBUTTONUP:
            self.mouseDragging = False

        elif events.type == pygame.MOUSEMOTION:
            if self.mouseDragging:
                self.titleCardRect.center = mousePos
            else:
                if self.isMouseInCard:
                    self.titleCardRect = self.titleCard.get_rect(center=self.titleCardRect.center)
                else:
                    self.titleCardRect = self.titleCard.get_rect(topleft=(575, 150))