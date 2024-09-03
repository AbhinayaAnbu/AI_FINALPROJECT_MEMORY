import random
import pygame
import sys
from pygame.locals import *

FPS = 30 
WINDOWWIDTH = 480  # Reduced window width
WINDOWHEIGHT = 360  # Reduced window height
REVEALSPEED = 8 
BOXSIZE = 40 
GAPSIZE = 10 
BOARDWIDTH = 6  # Reduced width
BOARDHEIGHT = 5  # Reduced height
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (0, 0, 0)

BGCOLOR = BLACK
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (LINES, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."

def main():
    global FPSCLOCK, DISPLAYSURF, mainBoard, revealedBoxes, player_score, ai_score, current_turn, firstSelection, is_player_turn

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Memory Game with AI')

    # Initialize game state
    player_score = 0
    ai_score = 0
    current_turn = 'player'  # Player starts first
    is_player_turn = True  # To track if it's the player's turn
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)
    firstSelection = None 

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True: 
        mousex, mousey = None, None
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)
        drawScore()

        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        if is_player_turn:
            if mousex is not None and mousey is not None:
                handle_player_click(mousex, mousey, mouseClicked)
        else:
            ai_move()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def handle_player_click(mousex, mousey, mouseClicked):
    global mainBoard, revealedBoxes, player_score, current_turn, firstSelection, is_player_turn

    if not is_player_turn:
        return

    boxx, boxy = getBoxAtPixel(mousex, mousey)
    if boxx is not None and boxy is not None:
        if not revealedBoxes[boxx][boxy] and mouseClicked:
            if firstSelection is None:
                firstSelection = (boxx, boxy)
                revealBoxesAnimation(mainBoard, [firstSelection])
                revealedBoxes[firstSelection[0]][firstSelection[1]] = True
            else:
                secondSelection = (boxx, boxy)
                if secondSelection == firstSelection:
                    return  # Ignore clicks on the same box

                revealBoxesAnimation(mainBoard, [secondSelection])
                revealedBoxes[secondSelection[0]][secondSelection[1]] = True

                icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                icon2shape, icon2color = getShapeAndColor(mainBoard, secondSelection[0], secondSelection[1])

                if icon1shape != icon2shape or icon1color != icon2color:
                    # No match
                    pygame.time.wait(1000)
                    coverBoxesAnimation(mainBoard, [firstSelection, secondSelection])
                    revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                    revealedBoxes[secondSelection[0]][secondSelection[1]] = False
                else:
                    # Match
                    player_score += 1
                    if hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        startGameAnimation(mainBoard)
                
                firstSelection = None
                current_turn = 'ai'
                is_player_turn = False

def ai_move():
    global mainBoard, revealedBoxes, ai_score, current_turn, is_player_turn

    if is_player_turn:
        return

    pygame.time.wait(1000)  # Simulate AI thinking time

    all_boxes = [(x, y) for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT) if not revealedBoxes[x][y]]
    if len(all_boxes) < 2:
        return  # Not enough boxes to make a move

    # AI picks two random boxes
    first_box, second_box = random.sample(all_boxes, 2)
    revealBoxesAnimation(mainBoard, [first_box, second_box])
    revealedBoxes[first_box[0]][first_box[1]] = True
    revealedBoxes[second_box[0]][second_box[1]] = True

    pygame.display.update()
    pygame.time.wait(1000)  # Simulate the time AI is thinking

    icon1shape, icon1color = getShapeAndColor(mainBoard, first_box[0], first_box[1])
    icon2shape, icon2color = getShapeAndColor(mainBoard, second_box[0], second_box[1])

    if icon1shape != icon2shape or icon1color != icon2color:
        # No match
        pygame.time.wait(1000)
        coverBoxesAnimation(mainBoard, [first_box, second_box])
        revealedBoxes[first_box[0]][first_box[1]] = False
        revealedBoxes[second_box[0]][second_box[1]] = False
    else:
        # Match
        ai_score += 1
        if hasWon(revealedBoxes):
            gameWonAnimation(mainBoard)
            pygame.time.wait(2000)
            mainBoard = getRandomizedBoard()
            revealedBoxes = generateRevealedBoxesData(False)
            drawBoard(mainBoard, revealedBoxes)
            pygame.display.update()
            pygame.time.wait(1000)
            startGameAnimation(mainBoard)

    current_turn = 'player'
    is_player_turn = True

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard():
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape, color))

    random.shuffle(icons) 
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2) 
    icons = icons[:numIconsUsed] * 2 
    random.shuffle(icons)

    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] 
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawIcon(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half =    int(BOXSIZE * 0.5) 

    left, top = leftTopCoordsOfBox(boxx, boxy) 
    
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))

def getShapeAndColor(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: 
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

def hasWon(revealedBoxes):
    for row in revealedBoxes:
        if False in row:
            return False 
    return True

def drawScore():
    font = pygame.font.Font(None, 36)
    scoreSurf = font.render(f'Player: {player_score}  AI: {ai_score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (10, WINDOWHEIGHT - 40)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

if __name__ == '__main__':
    main()
