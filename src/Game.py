import pygame as p
import ChessEngine
import os

p.init()
p.display.set_caption('Chess')

WIDTH = HEIGHT = 512
DIMENSION = 8 # 8x8 board
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

#Stackover flow solution for loading image problem
current_path = os.path.dirname(__file__) # Where your .py file is located
image_path = os.path.join(current_path, 'images') # The resource folder path


def loadImages():
    pieces = ['wp','bp','wB','bB','wK','bK','wN','bN','wQ','bQ','wR','bR']
    for piece in pieces:    
        IMAGES[piece] = p.transform.scale((p.image.load(os.path.join(image_path, str(piece)+'.png'))), (SQ_SIZE, SQ_SIZE))


def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #Flag variable
    loadImages()  #ONLY ONCE
    running = True
    sqSelected = () #No of square selected, keep track of the last click of the user (tuple(row, col))
    playerClicks = [] #keep track of player clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            #mouse event handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row,col): #Checking if user clicked the same square twice
                    sqSelected = () #Deselect the square
                
                else:    
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) #append both first and second click
                
                if len(playerClicks) == 2: #after 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):    
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            sqSelected = () # reset the user clicks
                            playerClicks = [] # reset the user clicks
                    if not moveMade:
                        playerClicks = [sqSelected]
            
            #key handlersz
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  #undo when z key is pressed
                    gs.undo()
                    moveMade = True
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

#Highlight square selected and moves for piece selected
def hightlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparency value scale of 0 to 255
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))




def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)   #draw squares on the board
    hightlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw the pieces on the board


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
 
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)] #picks even or odd box to color them
            p.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))  # bug was here!! no need to use p.rect()!


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--': #empty squares
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Animating a move
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of coordinates that the animation will move to
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10 #frames to move one square
    frameCount = (abs(dR)+abs(dC)) * framePerSquare
    for frame in range(frameCount+1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece move from its ending square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw the moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)
    



if __name__ == "__main__":
    main()