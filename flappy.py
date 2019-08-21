from itertools import cycle
import random
import sys
import os
import pygame
from pygame.locals import *
import pygbutton.pygbutton as pygbutton
import api
from pillow import ImageFont

font = ImageFont.truetype('times.ttf', 12)
size = font.getsize('Hello world')
print(size)

pygame.init()

COLOR_INACTIVE = pygame.Color('white')
COLOR_ACTIVE = pygame.Color('black')
COLOR_MISSED = pygame.Color('red')

FONT = pygame.font.Font(None, 32)
sFONT = pygame.font.Font(None, 20)
FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

largeFont = 0
mediumFont = 0
smallFont = 0

playerFlapAcc = -9  # players speed on flapping
playerMaxVelY = 10  # max vel along Y, max descend speed
playerRot = 45  # player's rotationG
playerVelRot = 3  # angular speed

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


class InputBox:

    def __init__(self, x, y, w, h, text='', bgcolor=False):

        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.textcolor = COLOR_INACTIVE
        self.fillcolor = COLOR_ACTIVE
        self.text = text
        self.placeholder = text
        self.txt_surface = FONT.render(text, True, self.textcolor)
        self.active = False
        self.clear_txt = True
        self.revert = False
        self.font_size = 32
        self.bgcolor = bgcolor
        self.cursor = 0
        self.lines = []
        self.offset = 0
        self.length = 0
        self.screen_cursor = 0
        self.clock = pygame.time.Clock()


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pygame.KEYDOWN:
            if self.clear_txt and self.active:
                self.text = ''
                self.clear_txt = False

            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.cursor -= 1
                else:
                    self.text += event.unicode
                if self.bgcolor:
                    if event.key == pygame.K_UP:
                        self.offset += 1
                    if event.key == pygame.K_DOWN:
                        self.offset -= 1

                if (len(self.text)*self.font_size) > 450:
                    self.font_size -= 2

                if 400 < (len(self.text)*self.font_size) < 450:
                    self.font_size += 2

            if not self.bgcolor:
                FONT_change = pygame.font.Font(None, self.font_size)
                # Re-render the text.
                self.txt_surface = FONT_change.render(self.text, True, self.textcolor)

                self.revert = True
            else:
                self.txt_surface = FONT.render(self.text, True, self.textcolor)

        if self.text == '' and self.revert and not self.active:
            self.txt_surface = FONT.render(self.placeholder, True, self.textcolor)
            self.clear_txt = True
            self.revert = False

    def update(self):
        if self.bgcolor:
            self.rect.w = SCREENWIDTH
        else:
            # Resize the box if the text is too long.
            width = max(200, self.txt_surface.get_width()+10)
            self.rect.w = width

    def draw(self, screen):
        if self.bgcolor:
            # Blit the rect.
            pygame.draw.rect(screen, self.fillcolor, self.rect, 0)
        else:
            pygame.draw.rect(screen, self.color, self.rect, 2)

        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        if int(pygame.time.get_ticks()/500) % 2 == 0 and self.active:
            for x in range(0, 5):
                screen.blit(FONT.render("|", True, self.textcolor),
                            (len(self.text)*self.font_size, self.rect.y))

        self.clock.tick(30)

def main():
    global SCREEN, FPSCLOCK
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    # SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Flappy Bird')

    global largeFont
    global mediumFont
    global smallFont

    global playerFlapAcc,playerMaxVelY,playerRot,playerVelRot
    playerFlapAcc = -9  # players speed on flapping
    playerMaxVelY = 10
    playerRot = 45  # player's rotation
    playerVelRot = 3  # angular speed

    largeFont = pygame.font.Font(
        os.path.join("res", "fonts", 'D:\\Github\\FlapPyBird\\assets\\sprites\\FlappyBirdy.ttf'),
        90)
    mediumFont = pygame.font.Font(
        os.path.join("res", "fonts", 'D:\\Github\\FlapPyBird\\assets\\sprites\\FlappyBirdy.ttf'),
        60)
    smallFont = pygame.font.Font(
        os.path.join("res", "fonts", 'D:\\Github\\FlapPyBird\\assets\\sprites\\FlappyBirdy.ttf'),
        40)

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[0]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showNextScreen(crashInfo)
        movementInfo = showChooseVariableAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    input_box1 = InputBox(50, 150, 50, 32, 'Full Name')
    input_box2 = InputBox(50, 200, 140, 32, 'Email')
    input_box3 = InputBox(50, 250, 140, 32, 'Phone Number')
    input_box4 = InputBox(50, 300, 140, 32, 'School')
    input_boxes = [input_box1, input_box2, input_box3, input_box4]
    buttonObj = pygbutton.PygButton((100, 350, 100, 30), 'Start')
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if 'click' in buttonObj.handleEvent(event):
                missed = False
                for box in input_boxes:
                    if box.text == box.placeholder:
                        box.color = COLOR_MISSED
                        missed = True
                    if box.placeholder == "Phone Number":
                        if not any(char.isdigit() for char in box.text):
                            box.color = COLOR_MISSED
                            missed = True
                    if box.placeholder == "Email":
                        if not box.text.__contains__("@"):
                            box.color = COLOR_MISSED
                            missed = True
                # make first flap sound and return values for mainGame
                if not missed:
                    SOUNDS['wing'].play()
                    return {
                        'playery': playery + playerShmVals['val'],
                        'basex': basex,
                        'playerIndexGen': playerIndexGen,
                    }

            for box in input_boxes:
                box.handle_event(event)

        for box in input_boxes:
            box.update()

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx+50, playery - 150 + playerShmVals['val']))
        SCREEN.blit(largeFont.render('Hack Floppy', 0, (255, 240, 230)), (10, 10))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        buttonObj.draw(SCREEN)  # where DISPLAYSURFACE was the Surface object returned from pygame.display.set_mode()
        for box in input_boxes:
            box.draw(SCREEN)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def birdJumpSpeed(text):
    global playerFlapAcc
    if text.isdigit():
        value = int(text)
        if value < 5:
            value = 5
        elif value > 15:
            value = 15

        playerFlapAcc = -value

    return


def birdFallSpeed(text):
    global playerMaxVelY

    if text.isdigit():
        value = int(text)
        if value < 1:
            value = 1
        elif value > 8:
            value = 8
        playerMaxVelY = value
    return


def birdSpinSpeed(text):
    global playerVelRot

    if text.isdigit():
        value = int(text)
        if value < 1:
            value = 1
        elif value > 8:
            value = 8
        playerVelRot = value
    return


def birdSpinAmount(text):
    global playerRot

    if text.isdigit():
        value = int(text)
        if value < 20:
            value = 20
        elif value > 65:
            value = 65
        playRot = value
    return


def showChooseVariableAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    global playerRot, playerVelRot, playerMaxVelY, playerFlapAcc
    playerVelY    =  -9 # player's velocity along Y, default same as playerFlapped
    playerMinVelY =  -8 # min vel along Y, max ascend speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9  # players speed on flapping
    playerFlapped = False # True when player flaps
    playerAccY = 1  # players downward accleration

    buttonObj1 = pygbutton.PygButton((25, 350, 110, 30), 'JumpSpeed')
    buttonObj2 = pygbutton.PygButton((25, 400, 110, 30), 'FallSpeed')
    buttonObj3 = pygbutton.PygButton((150, 350, 110, 30), 'SpinSpeed')
    buttonObj4 = pygbutton.PygButton((150, 400, 110, 30), 'SpinAmount')

    startButton = pygbutton.PygButton((85, 450, 100, 30), 'Start')
    buttons = {buttonObj1: [birdJumpSpeed, 0],
               buttonObj2: [birdFallSpeed, 1],
               buttonObj3: [birdSpinSpeed, 2],
               buttonObj4: [birdSpinAmount, 3]}

    input_box1 = InputBox(40, 300, 140, 32, '9')
    input_box2 = InputBox(40, 300, 140, 32, '3')
    input_box3 = InputBox(40, 300, 140, 32, '3')
    input_box4 = InputBox(40, 300, 140, 32, '45')
    input_boxes = [input_box1, input_box2, input_box3, input_box4]

    text_warning = ['Choose Value between 5 and 15',
                    'Choose Value between 1 and 8',
                    'Choose Value between 1 and 5',
                    'Choose Value between 20 and 60']

    warning = False
    text_box = False
    function = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if 'click' in startButton.handleEvent(event):
                SOUNDS['wing'].play()
                return {
                    'playery': playery,
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

            for box in input_boxes:
                box.handle_event(event)

            for button, list_ in buttons.items():
                button._propSetBgColor((212, 208, 200))
                if 'click' in button.handleEvent(event):
                    text_box = input_boxes[list_[1]]
                    warning = text_warning[list_[1]]
                    function = list_[0]


        if function:
            function(text_box.text)

        for box in input_boxes:
            box.update()

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        if playery > 250:
            playerVelY = playerFlapAcc
            playerFlapped = True

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(largeFont.render('Change', 0, (255, 240, 230)), (60, 10))
        SCREEN.blit(largeFont.render('variables', 0, (255, 240, 230)), (40, 60))
        if warning:
            SCREEN.blit(sFONT.render(warning, 0, (255, 240, 230)), (45, 335))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        SCREEN.blit(playerSurface, (playerx, playery))
        for buttonObj in buttons:
            buttonObj.draw(SCREEN)  # where DISPLAYSURFACE was the Surface object returned from pygame.display.set_mode()
        if text_box:
            text_box.draw(SCREEN)
        startButton.draw(SCREEN)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showChooseVariableAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    global playerRot, playerVelRot, playerMaxVelY, playerFlapAcc
    playerVelY    =  -9 # player's velocity along Y, default same as playerFlapped
    playerMinVelY =  -8 # min vel along Y, max ascend speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9  # players speed on flapping
    playerFlapped = False # True when player flaps
    playerAccY = 1  # players downward accleration

    input_box1 = InputBox(0, 300, 800, 1000, '9', True)

    text_warning = ['Choose Value between 5 and 15',
                    'Choose Value between 1 and 8',
                    'Choose Value between 1 and 5',
                    'Choose Value between 20 and 60']

    warning = False
    text_box = False
    function = False
    test = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if test:
                SOUNDS['wing'].play()
                return {
                    'playery': playery,
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

            input_box1.handle_event(event)

        input_box1.update()

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        if playery > 250:
            playerVelY = playerFlapAcc
            playerFlapped = True

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(largeFont.render('Change', 0, (255, 240, 230)), (60, 10))
        SCREEN.blit(largeFont.render('variables', 0, (255, 240, 230)), (40, 60))
        if warning:
            SCREEN.blit(sFONT.render(warning, 0, (255, 240, 230)), (45, 335))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        SCREEN.blit(playerSurface, (playerx, playery))
        input_box1.draw(SCREEN)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4
    global playerRot, playerVelRot, playerMaxVelY, playerFlapAcc
    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY    =  -9 # player's velocity along Y, default same as playerFlapped
    playerMinVelY =  -8 # min vel along Y, max ascend speed
    playerRotThr  =  20   # rotation threshold
    playerAccY = 1  # players downward accleration
    playerFlapped = False # True when player flaps


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showNextScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()

    buttonObj = pygbutton.PygButton((100, 350, 100, 30), 'HACK')

    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if 'click' in buttonObj.handleEvent(event):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        


        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(mediumFont.render('Time to Hack', 0, (255, 240, 230)), (50, 180))
        buttonObj.draw(SCREEN)

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx, playery))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()-20
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
