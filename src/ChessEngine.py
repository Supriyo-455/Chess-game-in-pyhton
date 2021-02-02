class GameState():
    def __init__(self):
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wK','wQ','wB','wN','wR']
        ]
        self.whiteToMove = True
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.movelog = []
        self.enpassantPossible = () #coordinates for the squares where an en passant capture is possible
        self.moveFunctions = {  'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                                'B':self.getBishopMoves,'K':self.getKingMoves,'Q':self.getQueenMoves    }

    '''
    Takes a move as a parameter and executes it (this will not work for castling , pawn promotion and en-passant)
    ''' 
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # swap players
        #update king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #If pawn moves twice , the next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()
        #if enpassant move must update the board to capture the pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn
        
        


    '''
    Undo last move
    '''
    def undo(self):
        if len(self.movelog)!=0: #make sure there is move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch characters back
            #update king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo 2 square pawn advanced
            if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
                self.enpassantPossible = ()
            


    '''
    All moves considering checks
    '''
    '''
                        Naive Algorithm 
                            def getValidMoves(self):
                                
                                #Naive solution
                                #1. Generate all the possible moves
                                moves = self.getAllPossibleMoves()
                                #2.For each move, make the move
                                for i in range(len(moves)-1, -1, -1): #when removing from the list go backwards through the list (bug safe)
                                    self.makeMove(moves[i])
                                    #3.Generate all opponent's moves
                                    #4.for each of your opponent's move, check if they attack your king
                                    self.whiteToMove = not self.whiteToMove
                                    if self.inCheck():
                                        moves.remove(moves[i]) #if they attack your king that's not a valid move
                                    self.whiteToMove = not self.whiteToMove
                                    self.undo()

                                if len(moves)==0: #either checkmate or stalemate
                                    if self.inCheck():
                                        self.checkmate = True
                                    else:
                                        self.stalemate = True
                                else:
                                    self.checkmate = False
                                    self.stalemate = False

                                return moves

                            #E coupling

                            #Determine if the current player is in check
                            def inCheck(self):
                                if self.whiteToMove:
                                    return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
                                else:
                                    return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

                            #Determine if the enemy can attack the square r,c
                            def squareUnderAttack(self,r,c):
                                self.whiteToMove = not self.whiteToMove #switch to opponent's turn
                                oppMoves = self.getAllPossibleMoves()
                                self.whiteToMove = not self.whiteToMove #switch the turns back
                                for move in oppMoves:
                                    if move.endRow == r and move.endCol == c: #that means the square is under attack
                                        return True
                                return False
                    
    '''

    #Advanced algorithm

    def getValidMoves(self):
        moves = []
        self.inCheck , self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only one check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the squares between the enemy piece and the king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking =  self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to
                #if knight, must captures the knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you to get to piece and checks
                            break

                #get rid of any moves that don't block check or move king
                for i in range(len(moves)-1,-1,-1): #Go through backwards when you are removing from the list
                    if moves[i].pieceMoved[1] != 'K': #move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block the check or capture the piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are valid
            moves = self.getAllPossibleMoves()
    

        return moves



    def checkForPinsAndChecks(self):
        pins = [] #squares where allied pinned piece is and direction pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        #Check outward from king for pins and checks, keep track of pins
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pin
            for i in range(1,8):
                endRow  = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #1st allied piece should be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities here in this complex conditional
                        #1) orthogonally away from king and piece is a rook
                        #2) diagonally away from king and piece is a bishop
                        #3) 1 square away from king diagonally and the piece is a pawn
                        #4) any direction and the piece is a queen
                        #5) any direction 1 square away from the king and the piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R')or(4 <= j <= 7 and type == 'B') or\
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7)or(enemyColor == 'b' and 4 <= j <= 5))) or\
                                (type == 'Q')or(i==1 and type == 'K'):
                            if possiblePin == (): #no piece blocking so check
                                inCheck = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece not applying check
                            break
                else: #off board
                    break

        #Check the knight moves
        knightMoves = ((-2,-1),(-2,1),(1,-2),(1,2),(-1,2),(-1,-2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece [1] == 'N': #enemy knight attacking the king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        
        return inCheck, pins, checks
       
    #All moves without considering checks
    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #No. of  rows
            for c in range(len(self.board[r])): #No. of col in a specific row
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) #For calling the appropiate functions of piece moves
        return moves            

    '''
    Get all the pawn moves for the pawn located at row,col and add these moves to list
    '''
    def getPawnMoves(self,r,c,moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == '--': #Empty square 1 square pawn advanced
                if not piecePinned or pinDirection == (-1,0):    
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r == 6 and self.board[r-2][c] == '--': #2 square pawn advanced
                        moves.append(Move((r,c),(r-2,c),self.board))
            #captures
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1,-1):    
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,enpassantPossible=True))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,enpassantPossible=True))
        
        else: #Black pawn moves
            if self.board[r+1][c] == '--': #Empty square 1 square pawn advanced
                if not piecePinned or pinDirection == (1,0):    
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r == 1 and self.board[r+2][c] == '--': #2 square pawn advanced
                        moves.append(Move((r,c),(r+2,c),self.board))
            #captures
            if c-1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    if not piecePinned or pinDirection == (1,-1):    
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,enpassantPossible=True))
            if c+1 <= 7: #captures to the right
                if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
                    if not piecePinned or pinDirection == (1,1):    
                        moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,enpassantPossible=True))
        
        #Add pawn promotions later

    '''
    Get all the rook moves for the pawn located at row,col and add these moves to list
    '''
    def getRookMoves(self,r,c,moves):
        
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cant't remove queen from pin on rook moves, only remove it on bishop moves    
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8): #Rooks can move maximum 7 blocks
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0<= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):    
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #empty space valid
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break

    '''
    Get all the knight moves for the pawn located at row,col and add these moves to list
    '''
    def getKnightMoves(self,r,c,moves):

        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        direction = ((-2,-1),(-2,1),(1,-2),(1,2),(-1,2),(-1,-2),(2,-1),(2,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in direction:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:    
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not an ally piece (empty space or enemy piece)
                        moves.append(Move((r,c),(endRow,endCol),self.board))

    '''
    Get all the bishop moves for the pawn located at row,col and add these moves to list
    '''
    def getBishopMoves(self,r,c,moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1,-1),(1,-1),(-1,1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8): #Bishops can move maximum 7 blocks
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0<= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):    
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #empty space valid
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break

    '''
    Get all the queen moves for the pawn located at row,col and add these moves to list
    '''
    def getQueenMoves(self,r,c,moves):
        
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    '''
    Get all the king moves for the pawn located at row,col and add these moves to list
    '''
    def getKingMoves(self,r,c,moves):
        
        direction = ((-1,-1),(1,-1),(-1,1),(1,1),(-1,0),(0,-1),(1,0),(0,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + direction[i][0]
            endCol = c + direction[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece (empty space or enemy piece)
                    #place king on the end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    #place king back to the original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)



class Move():

    #Rank file notation for a chess board
    ranksToRows = {'1':7, '2':6,'3':5, '4':4, '5':3, '6':2, '7':1, '8':0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCol = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    colsToFiles = {v:k for k,v in filesToCol.items()}

    def __init__(self,startSq, endSq, board, enpassantPossible = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        #pawn promotion
        self.isPawnPromotion = False
        if self.pieceMoved == 'wp' and self.endRow == 0:
            self.isPawnPromotion = True
        elif self.pieceMoved == 'bp' and self.endRow == 7:
            self.isPawnPromotion = True
        #en passant
        self.isEnpassantMove = enpassantPossible
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol 
    
    '''
    overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False
         

    def getChessNotation(self):
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]