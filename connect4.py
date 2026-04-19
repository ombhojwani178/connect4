import numpy as np
import pygame
import math
import sys
import random

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COL_COUNT = 7

SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)

WIDTH = COL_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT+1)*SQUARESIZE
size = (WIDTH,HEIGHT)

def create_board():
    board = np.zeros((ROW_COUNT,COL_COUNT))
    return board

def valid_location(board,col):
    return board[ROW_COUNT-1][col] == 0

def get_next_empty(board,col):
    for r in range(ROW_COUNT):
        if(board[r][col]==0):
         return r
    
def drop_piece(board,row,col,piece):
    board[row][col] = piece

def winning_move(board, piece):
    # Check horizontal for win
    for c in range(COL_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical for win
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COL_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COL_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


#AI HELPER FUNCTIONS
def get_valid_locations(board):
    valid_locations = []
    for col in range(COL_COUNT):
        if valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 # Assume opponent Player 1
    if piece == 1:
        opp_piece = 2

    # Score eval
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    # If op has 3 in a row, reduce score
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0
    
    # Prefer center column
    center_array = [int(i) for i in list(board[:, COL_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COL_COUNT-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COL_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Score Positive Diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COL_COUNT-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score Negative Diagonal
    for r in range(ROW_COUNT-3):
        for c in range(3, COL_COUNT):
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

#MINIMAX ALGORITHM
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    #Reached the depth limit or game over
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2): # AI wins
                return (None, 100000000000000)
            elif winning_move(board, 1): # Human wins
                return (None, -10000000000000)
            else: # drawn
                return (None, 0)
        else: # Reached depth limit, return score
            return (None, score_position(board, 2))
            
    if maximizingPlayer: # AI's turn
        value = -math.inf
        # Randomize initialcolumn choice
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_empty(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 2)
            
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            
            if new_score > value:
                value = new_score
                column = col
            
            # Alpha Beta Pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Human's turn 
        value = math.inf
        column = random.choice(valid_locations)
        
        for col in valid_locations:
            row = get_next_empty(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            
            if new_score < value:
                value = new_score
                column = col
                
            # Alpha-Beta Pruning
            beta = min(beta, value)
            if alpha >= beta:
                break 
        return column, value

def draw_board(board):
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE + SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    pygame.display.update()    

board = create_board()
game_over = False
turn = 0
pygame.init()
screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("Arial", 75)
while not game_over:
    
    #HUMAN EVENT LISTENER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # HOVER EFFECT
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

        # HUMAN CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE))
            
            # Player 1 Input HUMAN
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))
                
                if valid_location(board, col):
                    row = get_next_empty(board, col)
                    drop_piece(board, row, col, 1)

                    if winning_move(board, 1):
                        label = myfont.render("Human wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True

                    # Pass to AI
                    turn += 1
                    turn = turn % 2
                    draw_board(board)

    #2. AI TURN
    # Triggered automatically when turn == 1
    if turn == 1 and not game_over:
        
        # Call the Minimax funcn
        # if depth=5: Looks 5 moves ahead. 
        # -math.inf & math.inf: Starting values for Alpha and Beta.
        # True: It is the AI's turn to maximize the score.
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

        if valid_location(board, col):
            row = get_next_empty(board, col)
            drop_piece(board, row, col, 2)

            if winning_move(board, 2):
                label = myfont.render("AI wins!!", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over = True

            draw_board(board)
            
            # Pass turn to Human
            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(5000)