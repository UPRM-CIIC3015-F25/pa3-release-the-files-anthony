import pygame
from States.Core.StateClass import State
from Levels.LevelManager import LevelManager


class PlayerInfo(State):
    def __init__(self, nextState: str = ""):
        super().__init__(nextState)
        # ----------------------------Player Stats--------------------------------------------
        self.roundScore = 0                 # Current round score (depending on curSubLevel)
        self.playerChips = 0                # Current chip count
        self.playerMultiplier = 0           # Current score multiplier
        self.amountOfHands = 4              # Default number of hands
        self.amountOfDiscards = 4           # Default number of discards
        self.playerMoney = 0                # Current money
        self.playerAnte = 1                 # Current ante
        self.round = 1                      # Current round
        self.curHandOfPlayer = ""           # Current hand of the player
        self.curAmountJoker = "0"           # Current number of jokers used
        self.souls = 0                      # Yes, we adding dark souls in this bih (not quite... yet...)
        self.reviveCost = 5                 # Souls needed to revive
        self.canRevive = True               # Whether revive is available
        self.hasRevivedThisBlind = False    # Tracks is you have revived
        self.heat = 0                       # John Yakuzer
        self.heat_level = 0
        self.max_heat = 100
        self.isHeatActive = False
        self.heatDuration = 0


        
        # ----------------------------Level System--------------------------------------------
        self.levelManager = LevelManager(self)  # Must be after playerAnte is set ( DO NOT TOUCH THIS LINE )
        self.score = self.levelManager.curSubLevel.score  # Target score from current level
        self.levelFinished = False  # Flag to trigger level selection screen

        # --------------------------------Images----------------------------------------------
        self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
        self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        self.blindImage = self.levelManager.curSubLevel.image  # Get image from current level

        # -------------------------------Text Fonts-------------------------------------------
        self.textFont1 = pygame.font.Font('Graphics/Text/m6x11.ttf', 30)
        self.textFont2 = pygame.font.Font('Graphics/Text/m6x11.ttf', 22)
        self.textFont3 = pygame.font.Font('Graphics/Text/m6x11.ttf', 60)
        self.textFont4 = pygame.font.Font('Graphics/Text/m6x11.ttf', 25)

        # -------------------------------Text Renders-----------------------------------------
        self.scoreAtLeastText = self.textFont1.render("Score at least", False, 'white')
        self.scoreAtLeastTextNum = self.textFont3.render(str(self.score), False, 'red')
        self.playerScoreText = self.textFont3.render(str(self.roundScore), False, 'white')
        self.roundText = self.textFont2.render("Round", False, 'white')
        self.round2Text = self.textFont1.render("Round", False, 'white')
        self.scoreText = self.textFont2.render("Score", False, 'white')
        self.curHandText = self.textFont1.render(self.curHandOfPlayer, False, 'white')
        self.xText = self.textFont3.render('X', False, (180, 30, 30))
        self.runText = self.textFont1.render('Run', False, 'white')
        self.infoText = self.textFont1.render('Info', False, 'white')
        self.instrText = self.textFont1.render('Help', False, 'white')
        self.handText = self.textFont1.render('Hands', False, 'white')
        self.discardText = self.textFont4.render('Discards', False, 'white')
        self.anteText = self.textFont1.render("Ante", False, "white")
        self.anteLimitText = self.textFont1.render("/ 6", False, "white")

        # --------------------------------Rects-----------------------------------------------
        self.leftRect = pygame.Rect(0, 0, 300, 750)

        # --------------------Top Blind Section-----------------------------------------------
        self.blindRect = pygame.Rect(15, 15, 270, 200)
        self.blindTextRect = pygame.Rect(75, 60, 190, 120)
        self.blindRectImage = self.blindImage.get_rect(topleft=(5, 90))  # Renamed for clarity

        # --------------------Player Info Section---------------------------------------------
        self.playerInfo = pygame.Rect(15, 300, 270, 140)
        self.curHandTextRect = self.curHandText.get_rect()
        self.chipsRect = pygame.Rect(5, 55, 120, 80)
        self.multiplierRect = pygame.Rect(130, 55, 130, 80)
        self.xTextRect = pygame.Rect(115, 70, 0, 0)

        # --------------------Player Info 2 Section-------------------------------------------
        self.playerInfo2 = pygame.Rect(5, 450, 290, 270)
        self.runInfoRect = pygame.Rect(0, 0, 100, 125)
        self.runTextRect = pygame.Rect(25, 25, 75, 95)
        self.infoTextRect = pygame.Rect(20, 60, 0, 0)
        self.instrRect = pygame.Rect(0, 130, 100, 165)
        self.instrTextRect = pygame.Rect(15, 190, 0, 0)
        self.handRect = pygame.Rect(105, 15, 90, 85)
        self.discardRect = pygame.Rect(203, 15, 90, 85)

        # ------------------------------Surfaces----------------------------------------------
        self.scoreAtLeastTextSurf = pygame.Surface((190, 130), pygame.SRCALPHA)
        self.leftRectSurface = pygame.Surface((300, 750), pygame.SRCALPHA)
        self.blindRectSurface = pygame.Surface((270, 200), pygame.SRCALPHA)
        self.blindTextSurface = pygame.Surface((270, 400), pygame.SRCALPHA)
        self.playerInfoSurface = pygame.Surface((270, 140), pygame.SRCALPHA)
        self.playerInfo2Surface = pygame.Surface((290, 300), pygame.SRCALPHA)

        # --------------------Animation Variables for smallBlind-------------------------
        self.smallBlindAngle = 0  # Current angle of rotation
        self.smallBlindDirection = 1  # 1 = rotate right, -1 = rotate left
        self.smallBlindMaxAngle = 5  # Maximum rotation angle
        self.smallBlindSpeed = 0.15  # How fast it rotates

    def update(self):
        # Update smallBlind rotation
        self.smallBlindAngle += self.smallBlindDirection * self.smallBlindSpeed
        if abs(self.smallBlindAngle) >= self.smallBlindMaxAngle:
            self.smallBlindDirection *= -1  # Reverse direction when max angle reached

        # Update background based on whether current level is a boss level
        if self.levelManager.curSubLevel.bossLevel == "":
            self.backgroundImage = pygame.image.load('Graphics/Backgrounds/gameplayBG.jpg')
            self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        else:
            self.backgroundImage = pygame.image.load('Graphics/Backgrounds/bossBG.png')
            self.background = pygame.transform.scale(self.backgroundImage, (1300, 750))
        self.draw() # draw the updated player info panel

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        pygame.draw.rect(State.screen, (50, 50, 50), self.leftRect)
        pygame.draw.rect(State.screen, 'blue', self.leftRect, 1)
        self.leftRectSurface.fill((0, 0, 0, 0))
        self.drawbuttons()
        self.screen.blit(self.leftRectSurface, self.leftRect)
        mousePosPlayerInfo2 = (
        pygame.mouse.get_pos()[0] - self.playerInfo2.x, pygame.mouse.get_pos()[1] - self.playerInfo2.y)

        if self.runInfoRect.collidepoint(mousePosPlayerInfo2):
            pygame.draw.rect(self.playerInfo2Surface, (139, 0, 0), self.runInfoRect)
        else:
            pygame.draw.rect(self.playerInfo2Surface, 'red', self.runInfoRect)
        if self.instrRect.collidepoint(mousePosPlayerInfo2):
            pygame.draw.rect(self.playerInfo2Surface, 'darkorange', self.instrRect)
        else:
            pygame.draw.rect(self.playerInfo2Surface, 'orange', self.instrRect)

    def drawbuttons(self):
        # ------------------------Blind Section-------------------------------------------
        # Choose colors based on blind type, but override with boss-specific colors
        boss_colors = {
            "The Mark": ((120, 40, 160), (60, 30, 80)),        # purple
            "The Needle": ((180, 20, 20), (80, 20, 20)),       # crimson
            "The House": ((200, 160, 20), (100, 80, 10)),      # gold/bronze
            "The Hook": ((20, 150, 140), (10, 70, 80)),        # teal
            "The Water": ((30, 120, 200), (10, 50, 90)),       # blue
            "The Manacle": ((90, 90, 90), (40, 40, 40)),       # steel/gray
            "The Club": ((20, 120, 40), (10, 60, 30)),         # green
            "The Goad": ((70, 40, 140), (30, 20, 70)),         # indigo
        }

        # determine current sublevel and choose colors
        curSubLevel = self.levelManager.curSubLevel
        boss_name = self.levelManager.curSubLevel.bossLevel

        # check if boss level to set colors
        if boss_name and boss_name in boss_colors:
            header_color, bg_color = boss_colors[boss_name]
        else:
            # otherwise set based on blind type
            if curSubLevel.blind.name == "SMALL":
                header_color = (70, 130, 180)
                bg_color = (40, 65, 90)
            elif curSubLevel.blind.name == "BIG":
                header_color = (255, 140, 0)
                bg_color = (127, 70, 0)
            else:
                header_color = (128, 128, 128)
                bg_color = (64, 64, 64)

        # draw background rect for the blind area on the left panel
        pygame.draw.rect(self.leftRectSurface, bg_color, self.blindRect)
        # Clear the blind surface each frame to avoid leftover pixels/colors from previous frames
        self.blindRectSurface.fill((0, 0, 0, 0))
        self.blindTextSurface.fill((0, 0, 0, 0))  # Clear before redrawing

        # Header rectangle uses header_color
        pygame.draw.rect(self.blindRectSurface, header_color, pygame.Rect(0, 0, 270, 45))

        # Dynamic blind name Text (centered in the header area)
        cur = self.levelManager.curSubLevel
        if cur.bossLevel:
            label = cur.bossLevel
        else:
            label = cur.blind.name

        textBlindDynamic = self.textFont1.render(label, True, 'white')

        header_height = 45
        header_center = (self.blindRectSurface.get_width() // 2, header_height // 2)
        text_rect = textBlindDynamic.get_rect(center=header_center)
        # draw directly on the blindRectSurface so it is centered in the header
        self.blindRectSurface.blit(textBlindDynamic, text_rect)
        # optional small dark bar below header for contrast
        pygame.draw.rect(self.blindRectSurface, (30, 30, 30), self.blindTextRect)

        # ------------------------Score Section-------------------------------------------
        pygame.draw.rect(self.leftRectSurface, (30, 30, 30), pygame.Rect(15, 220, 270, 70))
        pygame.draw.rect(self.leftRectSurface, (0, 0, 0), pygame.Rect(110, 225, 160, 60))
        # display roundScore here (updated by GameState.playHand)
        playerScoreStr = self.textFont3.render(str(self.roundScore), False, 'white')

        playerScoreStrRect = playerScoreStr.get_rect()
        playerScoreStrRect.right = 265
        playerScoreStrRect.top = 230

        # Dynamic score target from current level
        scoreAtLeastTextNum = self.textFont3.render(str(self.levelManager.curSubLevel.score), False, 'red')
        scoreAtLeatTextNumRect = scoreAtLeastTextNum.get_rect()
        scoreAtLeatTextNumRect.center = (100, 70)

        # --------------------Player Info Section-----------------------------------------
        pygame.draw.rect(self.leftRectSurface, (30, 30, 30), self.playerInfo)
        pygame.draw.rect(self.playerInfoSurface, 'blue', self.chipsRect)
        pygame.draw.rect(self.playerInfoSurface, 'red', self.multiplierRect)

        playerChipsText = self.textFont3.render(str(self.playerChips), True, 'white')
        playerMultiplierText = self.textFont3.render(str(self.playerMultiplier), True, 'white')

        playerChipsTextRect = playerChipsText.get_rect()
        playerMultiplierTextRect = playerMultiplierText.get_rect()
        playerChipsTextRect.right = 100
        playerMultiplierTextRect.left = 180
        playerChipsTextRect.y = 70
        playerMultiplierTextRect.y = 70

        self.playerInfoSurface.blit(playerChipsText, playerChipsTextRect)
        self.playerInfoSurface.blit(playerMultiplierText, playerMultiplierTextRect)
        self.playerInfoSurface.blit(self.xText, self.xTextRect)

        # ---------------------Player Info 2 Section--------------------------------------
        pygame.draw.rect(self.playerInfo2Surface, (20, 20, 20), self.handRect)
        pygame.draw.rect(self.playerInfo2Surface, (20, 20, 20), self.discardRect)

        # ---------------------Hands------------------------------------------------------
        self.playerInfo2Surface.blit(self.handText, pygame.Rect(120, 18, 0, 0))
        pygame.draw.rect(self.playerInfo2Surface, (30, 30, 30), pygame.Rect(110, 45, 80, 50))
        amountsOfHandsText = self.textFont3.render(str(self.amountOfHands), False, 'blue')
        self.playerInfo2Surface.blit(amountsOfHandsText, pygame.Rect(140, 50, 0, 0))

        # ---------------------Discards---------------------------------------------------
        self.playerInfo2Surface.blit(self.discardText, pygame.Rect(208, 18, 0, 0))
        pygame.draw.rect(self.playerInfo2Surface, (30, 30, 30), pygame.Rect(207, 45, 80, 50))
        amountOfDiscardsText = self.textFont3.render(str(self.amountOfDiscards), False, 'red')
        self.playerInfo2Surface.blit(amountOfDiscardsText, pygame.Rect(235, 50, 0, 0))

        # ---------------------Player Money-----------------------------------------------
        pygame.draw.rect(self.playerInfo2Surface, (20, 20, 20), pygame.Rect(105, 110, 185, 70))
        pygame.draw.rect(self.playerInfo2Surface, (30, 30, 30), pygame.Rect(112, 118, 170, 55))
        playerMoneyText = self.textFont3.render("$ " + str(self.playerMoney), False, (255, 215, 0))
        playerMoneyTextRect = playerMoneyText.get_rect()
        playerMoneyTextRect.center = (200, 150)
        self.playerInfo2Surface.blit(playerMoneyText, playerMoneyTextRect)

        # -----------------------Ante-----------------------------------------------------
        pygame.draw.rect(self.playerInfo2Surface, (20, 20, 20), pygame.Rect(105, 190, 90, 100))
        pygame.draw.rect(self.playerInfo2Surface, (30, 30, 30), pygame.Rect(110, 220, 80, 65))
        self.playerInfo2Surface.blit(self.anteText, pygame.Rect(122, 195, 0, 0))
        self.playerInfo2Surface.blit(self.anteLimitText, pygame.Rect(155, 245, 0, 0))
        playerAnteText = self.textFont3.render(str(self.playerAnte), False, 'orange')
        self.playerInfo2Surface.blit(playerAnteText, pygame.Rect(125, 230, 0, 0))

        # -----------------------Round----------------------------------------------------
        pygame.draw.rect(self.playerInfo2Surface, (20, 20, 20), pygame.Rect(200, 190, 90, 100))
        pygame.draw.rect(self.playerInfo2Surface, (30, 30, 30), pygame.Rect(205, 220, 80, 65))
        self.playerInfo2Surface.blit(self.round2Text, pygame.Rect(215, 195, 0, 0))
        playerRoundText = self.textFont3.render(str(self.round), False, 'orange')
        self.playerInfo2Surface.blit(playerRoundText, pygame.Rect(235, 230, 0, 0))

        # ------------------Join all surfaces---------------------------------------------
        self.scoreAtLeastTextSurf.fill((0, 0, 0, 0))  # Clear before redrawing
        self.scoreAtLeastTextSurf.blit(self.scoreAtLeastText, pygame.Rect(15, 0, 10, 10))
        self.scoreAtLeastTextSurf.blit(scoreAtLeastTextNum, scoreAtLeatTextNumRect)

        self.blindRectSurface.blit(self.scoreAtLeastTextSurf, self.blindTextRect)
        self.blindRectSurface.blit(self.blindTextSurface, self.blindRect)

        # --------------------Blind Image Rotation Animation (Dynamic)-------------------------------
        self.blindImage = self.levelManager.curSubLevel.image  # Update image each frame
        rotatedBlindImage = pygame.transform.rotate(self.blindImage, self.smallBlindAngle)
        rotatedRect = rotatedBlindImage.get_rect(center=self.blindRectImage.center)
        self.blindRectSurface.blit(rotatedBlindImage, rotatedRect.topleft)

        # Now that blindRectSurface is fully drawn for this frame, blit it to the left panel
        self.leftRectSurface.blit(self.blindRectSurface, self.blindRect)

        self.playerInfo2Surface.blit(self.runText, self.runTextRect)
        self.playerInfo2Surface.blit(self.infoText, self.infoTextRect)
        self.playerInfo2Surface.blit(self.instrText, self.instrTextRect)
        self.playerInfo2Surface.blit(self.playerInfo2Surface, self.playerInfo2)

        self.leftRectSurface.blit(self.roundText, pygame.Rect(30, 230, 20, 20))
        self.leftRectSurface.blit(self.scoreText, pygame.Rect(30, 250, 20, 20))
        self.leftRectSurface.blit(playerScoreStr, playerScoreStrRect)
        self.leftRectSurface.blit(self.playerInfoSurface, self.playerInfo)
        self.leftRectSurface.blit(self.playerInfo2Surface, self.playerInfo2)

    def userInput(self, events): # Handle user input
        # Get mouse position relative to playerInfo2Surface
        mousePos = pygame.mouse.get_pos()
        mousePosPlayerInfo2 = (mousePos[0] - self.playerInfo2.x, mousePos[1] - self.playerInfo2.y)
        
        # Change next state based on user input
        if events.type == pygame.QUIT:
            self.isFinished = True
            self.nextState = "StartState"
        if events.type == pygame.KEYDOWN and events.key == pygame.K_ESCAPE:
            self.isFinished = True
            self.nextState = "StartState"
        if events.type == pygame.MOUSEBUTTONDOWN:
            if self.runInfoRect.collidepoint(mousePosPlayerInfo2):
                self.buttonSound.play()
                self.isFinished = True
                self.nextState = "RunInfoState"
            if self.instrRect.collidepoint(mousePosPlayerInfo2):
                self.buttonSound.play()