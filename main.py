import pygame
from scripts import *

class player():
    '''
    Player class object which keeps the score.
    '''
    def __init__(self, idx, name, colour):
        self.idx = idx
        self.name = str(name)
        self.colour = str(colour)
        self.score = 0
        self.tally = []
        
    def reset_player(self):
        self.score = 0
        self.tally = []
        

class TheGame():
    
    def __init__(self, nrows, ncols, width=20, margin=4):
        '''
        Initialising the game and defining the board size parameters.
        '''
        self.nrows = nrows
        self.ncols = ncols
        self.width = width
        self.margin = margin#//2*2
        self.full_width = self.width + self.margin
        self.size = (self.ncols*self.full_width + self.margin + 300 + 139*0,
                     self.nrows*self.full_width + self.margin + 6*0)
        self.reset_state()
        self.colours = {
            'BLACK': (0, 0, 0),
            'GREY': (220, 220, 220),
            'WHITE': (255, 255, 255),
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'ORANGE': (255, 165, 0),
            'BROWN': (165,42,42)
        }

    def reset_state(self):
        '''
        Creating 3 arrays that store the board status, such as ownership of the tiles and border locations.
        
        And reseting some other temp variables.
        '''
        self.grid = np.zeros([self.nrows, self.ncols], dtype=int)
        self.rows = np.ones([self.nrows-1, self.ncols], dtype=int)*7
        self.cols = np.ones([self.nrows, self.ncols-1], dtype=int)*7
        self.play_again = 0
        self.done = 0
        self.winner = ''
        self.selection = ()
        self.get_remaining_moves()
        
        
    def create_players(self, kwargsP1, kwargsP2):
        '''
        Creating the players and a switch toggle between them.
        '''
        self.p1 = player(idx=1, **kwargsP1)
        self.p2 = player(idx=2, **kwargsP2)
        self.players = {1: self.p2, 2: self.p1}
        self.active_player = self.p1
    
    def update_scores(self, player):
        '''
        This function runs after every move.
        
        It checks if the newly drawn border partitioned the board in such
        a way that some tiles need to be attributed to the active player.
        '''
        mgrid = merge(self.grid, self.rows, self.cols) # merging tiles with borders
        ccs = get_cc(mgrid)                            # finding all connected and unclaimed areas (connected components)
        sizes = [len(x) for x in ccs]                  # getting their sizes
        maks = np.argmax(sizes)                        # identifying the largest area
        
        # attributing all but the largest area to the active player 
        ccs = np.delete(ccs, maks, axis=0)
        score = 0
        for i in range(len(ccs)):
            for j in ccs[i]:
                mgrid[j[0], j[1]] = player.idx
                score += 1
                
        # updating players score
        if score > 0:
            player.score += score
            player.tally.append(score)
            
        # updating the board with new ownership
        self.grid, self.rows, self.cols = split(mgrid)
        self.get_remaining_moves()
        self.check_winning_conditions(player)
        
    def get_remaining_moves(self):
        '''
        This functions checks remaining possible moves and stores them.
        '''

        # get remaining row moves
        row_moves = []
        for r in range(self.rows.shape[0]):
            for c in range(self.rows.shape[1]-2):
                if (self.rows[r, c:c+3] == np.array([7, 7, 7])).all():
                    row_moves.append([r, c])

        remaining_row_moves = []
        mgrid = merge(self.grid, self.rows, self.cols)
        for r, c in row_moves:
            r = r*2+1
            c = c*2
            if (mgrid[r-1:r+2, c:c+5]==0).any():
                remaining_row_moves.append([int((r-1)/2), int(c/2)])


        # get remaining col moves     
        col_moves = []
        for r in range(self.cols.shape[0]-2):
            for c in range(self.cols.shape[1]):
                if (self.cols[r:r+3, c] == np.array([7, 7, 7])).all():
                    col_moves.append([r, c])

        remaining_col_moves = []
        mgrid = merge(self.grid, self.rows, self.cols)
        for r, c in col_moves:
            r = r*2
            c = c*2+1
            if (mgrid[r:r+5, c-1:c+2]==0).any():
                remaining_col_moves.append([int(r/2), int((c-1)/2)])

        self.rrm = remaining_row_moves
        self.rcm = remaining_col_moves
        
    
    def check_winning_conditions(self, player):
        '''
        Checks the winning conditions and declares the winner or a draw
        '''
        # if a player controls more than half of the tiles game is over
        if player.score > self.grid.size/2:
            self.done = 1
        # if there are no moves left, game is over
        elif self.rrm==[] and self.rcm==[]:
            self.done = 1
        
        if self.done==1:
            self.selection = ()
            if self.p1.score==self.p2.score:
                self.winner = 'Draw'
            elif self.p1.score > self.p2.score:
                self.winner = self.p1
            else:
                self.winner = self.p2             
            
        
    def draw_line(self, player):
        '''
        Draws the new border line, updates the score and switches the player.
        '''
        if [len(x) for x in self.selection]==[1, 3]:
            self.rows[self.selection] = 8
            self.update_scores(player)
            self.active_player = self.players[player.idx]
        elif [len(x) for x in self.selection]==[3, 1]:
            self.cols[self.selection] = 8
            self.update_scores(player)
            self.active_player = self.players[player.idx]
            
    def draw_board(self, display, mouse, event):
        '''
        This function takes care of all the visuals in the game.
        '''
        
        ### Draw the foundation ---------------------###
        ###------------------------------------------###
        
        tile_colour = self.colours['WHITE']
        border_colour = self.colours['BLACK']
        highlight_colour = self.colours['GREEN']
        display.fill(self.colours['BLACK'])
        
        # filling the game area
        pygame.draw.rect(display, self.colours['GREY'],
                                 [self.margin, self.margin,
                                  self.full_width*self.ncols - self.margin,
                                  self.full_width*self.nrows - self.margin])
        
        # filling the scores area
        pygame.draw.rect(display, self.colours['GREY'],
                                 [self.full_width*self.ncols + self.margin*2,
                                  self.margin, 300 - + self.margin*3,
                                  self.full_width*self.nrows - self.margin])
        
        # top horizontal black line
        pygame.draw.rect(display, self.colours['BLACK'],
                                 [self.full_width*self.ncols + self.margin*2,
                                  self.margin*7, 300 - + self.margin*3,
                                  self.margin/2])
        
        # bottom horizontal black line
        pygame.draw.rect(display, self.colours['BLACK'],
                                 [self.full_width*self.ncols + self.margin*2,
                                  self.margin*11, 300 - + self.margin*3,
                                  self.margin/2])
        
        
        ### Draw the scoreboard ---------------------###
        ###------------------------------------------###
        
        font24 = pygame.font.SysFont('dejavusansmono', 24)
        font36 = pygame.font.SysFont('dejavusansmono', 36)
        font48 = pygame.font.SysFont('dejavusansmono', 48)
        
        # draw active player indication
        star = font36.render('*', True, self.active_player.colour)
        display.blit(star, dest=(self.full_width*self.ncols + self.margin*2 + 67.5 - star.get_rect().width / 2 + 135*(self.active_player.idx-1), self.margin*0.8))
        
        for p in list(self.players.values()):
            name = font36.render(p.name, True, p.colour)
            score = font36.render(str(p.score), True, p.colour)
            
            display.blit(name, dest=(self.full_width*self.ncols + self.margin*2 + 67.5 + 135*(p.idx-1) - name.get_rect().width / 2, self.margin*2.7))
            display.blit(score, dest=(self.full_width*self.ncols + self.margin*2 + 67.5 + 135*(p.idx-1) - score.get_rect().width / 2, self.margin*7.1))
            
            offset = 0
            for t in list_columns(p.tally, rows=int(self.nrows*1.5-3)):
                tally = font24.render(t, True, p.colour)
                display.blit(tally, dest=(self.full_width*self.ncols + self.margin*2 + 67.5 + 135*(p.idx-1) - tally.get_rect().width / 2, self.margin*12 + offset))
                offset += 30
                
        
        ### Draw the game board ---------------------###
        ###------------------------------------------###
        
        # draw the tiles
        for row in range(self.nrows):
            for col in range(self.ncols):
                value = self.grid[row, col]
                colour = [tile_colour, self.p1.colour, self.p2.colour][value]
                pygame.draw.rect(display, colour,
                                 [self.full_width*col + self.margin,
                                  self.full_width*row + self.margin,
                                  self.width, self.width])

        # draw the row borders
        row_borders = np.array(np.where(self.rows==8)).T
        for i in row_borders:
            pygame.draw.rect(display, border_colour,
                             [self.full_width*i[1] + self.margin/2,
                              self.full_width*i[0] + self.full_width,
                              self.full_width, self.margin])

        # draw the col borders
        col_borders = np.array(np.where(self.cols==8)).T
        for i in col_borders:
            pygame.draw.rect(display, border_colour,
                             [self.full_width*i[1] + self.full_width,
                              self.full_width*i[0] + self.margin/2,
                              self.margin, self.full_width])
            
            
        ### Draw the current selection --------------###
        ###------------------------------------------###
        
        if self.done==0:
        
            self.selection = ()
            c = (mouse[0] - self.margin/2) / self.full_width
            r = (mouse[1] - self.margin/2) / self.full_width
            distancetocol = np.abs(np.round(c) - c)
            distancetorow = np.abs(np.round(r) - r)


            # highlighting the closest three piece row or column border
            if distancetorow < distancetocol:
                rr = int(np.round(r))
                rc = int(np.round(c - 1.5))
                rect = [0, 0, 0, 0]
                if [rr-1, rc] in self.rrm:
                    rect = [rc*self.full_width,
                            rr*self.full_width,
                            self.margin + 3*self.full_width, self.margin]     
                    self.selection = ([rr-1], list(range(rc, rc+3)))

            else:
                rr = int(np.round(r - 1.5))
                rc = int(np.round(c))
                rect = [0, 0, 0, 0]
                if [rr, rc-1] in self.rcm:
                    rect = [np.round(c)*self.full_width,
                            np.round(r - 1.5)*self.full_width,
                            self.margin, self.margin + 3*self.full_width]
                    self.selection = (list(range(rr, rr+3)), [rc-1])

            pygame.draw.rect(display, highlight_colour, rect)
        
        
        ### Draw the winning screen -----------------###
        ###------------------------------------------###
        
        else:
            
            # creating the popup table
            pygame.draw.rect(display, self.colours['GREEN'],
                             [self.full_width*self.ncols/2 - self.full_width*3,
                              self.full_width*self.nrows/2 - self.full_width*2,
                              self.full_width*6 + self.margin,
                              self.full_width*4 + self.margin])
                
            pygame.draw.rect(display, self.colours['ORANGE'],
                             [self.full_width*self.ncols/2 + self.margin/2 - self.full_width*3,
                              self.full_width*self.nrows/2 + self.margin/2 - self.full_width*2,
                              self.full_width*6,
                              self.full_width*4])
            
            pygame.draw.rect(display, self.colours['BLACK'],
                             [self.full_width*self.ncols/2 + self.margin/2 - self.full_width*2,
                              self.full_width*self.nrows/2 + self.margin/2 + self.full_width*0.5,
                              self.full_width*4,
                              self.full_width*1],
                             3)
            
            # text box "player x wins"
            outcome_text = font48.render(f'{self.winner.name} wins!', True, self.winner.colour)
            display.blit(outcome_text, dest=(self.full_width*self.ncols/2 + self.margin/2 - outcome_text.get_rect().width / 2,
                                             self.full_width*self.nrows/2 + self.margin*1.5 - self.full_width - outcome_text.get_rect().height / 2))
            
            # text box "play again"
            play_again_text = font24.render('Play again', True, self.colours['BLACK'])
            display.blit(play_again_text, dest=(self.full_width*self.ncols/2 + self.margin/2 - play_again_text.get_rect().width / 2,
                                             self.full_width*self.nrows/2 + self.margin/2 + self.full_width - play_again_text.get_rect().height / 2))
            
            self.play_again = 0
            if  mouse[0] > self.full_width*self.ncols/2 + self.margin/2 - self.full_width*2 and \
                mouse[0] < self.full_width*self.ncols/2 + self.margin/2 + self.full_width*2 and \
                mouse[1] > self.full_width*self.nrows/2 + self.margin/2 + self.full_width*0.5 and \
                mouse[1] < self.full_width*self.nrows/2 + self.margin/2 + self.full_width*1.5:
                pygame.draw.rect(display, self.colours['GREEN'],
                                 [self.full_width*self.ncols/2 + self.margin/2 - self.full_width*2,
                                  self.full_width*self.nrows/2 + self.margin/2 + self.full_width*0.5,
                                  self.full_width*4,
                                  self.full_width*1],
                                 3)
                self.play_again = 1
                
                
                
######################################################################################################################

pygame.init()
pygame.display.set_caption('BorderConquest')
aGame = TheGame(10, 10, width=34, margin=9)
aGame.create_players({'name':'P1', 'colour':'RED'}, {'name':'P2', 'colour':'BLUE'})
display = pygame.display.set_mode(aGame.size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if aGame.play_again==1:
                aGame.reset_state()
                for p in list(aGame.players.values()):
                    p.reset_player()
            else:
                aGame.draw_line(aGame.active_player)        

    # Draw the game
    aGame.draw_board(display, pygame.mouse.get_pos(), event)
    pygame.display.update()