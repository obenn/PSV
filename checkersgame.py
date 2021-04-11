import random
from collections.abc import Iterable

class Piece:
    def __init__(self, colour):
        self.colour = colour
        self.king = False

    
    def __str__(self):
        if self.colour == 'black':
            return 'B' if self.king else 'b'
        else:
            return 'W' if self.king else 'w'


class Cell:
    def __init__(self, index, piece, game):
        self.index = index
        self.piece = piece
        self.game = game
        self.above = None
        self.below = None
    
    def possible_jumps(self, colour, king, exclude=[]):
        jumps = []
        if colour == 'black' or king:
            for i in (0, 1):
                if self.above[i] and self.above[i].piece and self.above[i].piece.colour != colour:
                    if self.above[i].above[i] and self.above[i].above[i].piece == None:
                        if self.above[i] not in exclude:
                            jumps.append((self.above[i], self.above[i].above[i]))
        if colour == 'white' or king:
            for i in (0, 1):
                if self.below[i] and self.below[i].piece and self.below[i].piece.colour != colour:
                    if self.below[i].below[i] and self.below[i].below[i].piece == None:
                        if self.below[i] not in exclude:
                            jumps.append((self.below[i], self.below[i].below[i]))
        return jumps
        
    
    def possible_moves(self, colour, king):
        moves = []
        if colour == 'black' or king:
            for i in (0, 1):
                if self.above[i] and not self.above[i].piece:
                    moves.append(self.above[i])
        if colour == 'white' or king:
            for i in (0, 1):
                if self.below[i] and not self.below[i].piece:
                    moves.append(self.below[i])
        return moves
    
    def valid_moves(self):
        return [(self.index, c.index) for c in self.possible_moves(self.piece.colour, self.piece.king)]
    
    def valid_jumps(self):
        jump_paths = [[j] for j in self.possible_jumps(self.piece.colour, self.piece.king)]
        done = False
        while not done:
            jump_paths_new = []
            for path in jump_paths:
                npaths = path[-1][1].possible_jumps(self.piece.colour, self.piece.king, exclude=[p[0] for p in path])
                if npaths:
                    for p in npaths:
                        jump_paths_new.append(path + [p])
                else:
                    jump_paths_new.append(path)
            if len(jump_paths_new) == len(jump_paths):
                done = True
            jump_paths = jump_paths_new
        paths = []
        for p in jump_paths:
            paths.append((self.index, tuple((s.index, d.index) for s, d in p)))
        return paths

    def do_move(self, move):
        if isinstance(move, int):
            c = self.game.board[move]
            c.piece = self.piece
            self.piece = None
        else:
            c = self
            for j in move:
                self.game.board[j[0]].piece = None
                self.game.board[j[1]].piece = c.piece
                c.piece = None
                c = self.game.board[j[1]]

        if (c.piece.colour == 'white' and c.index < 4) or (c.piece.colour == 'black' and c.index > 27):
            c.piece.king = True
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.piece:
            return f'[{self.piece}]'
        return '[X]'

class Game:
    def __init__(self, turn='black'):

        black_pieces = [Piece('black') for _ in range(12)]
        white_pieces = [Piece('white') for _ in range(12)]
        board = [Cell(i, p, self) for i, p in enumerate(self.black_pieces + ([None]*8) + self.white_pieces)]

        for i in range(len(board)):
            if i % 8 == 3:
                board[i].above = (None, board[i + 4])
                if i > 3:
                    board[i].below = (None, board[i - 4])
                else:
                    board[i].below = (None, None)
            elif i % 8 == 4:
                if i < 28:
                    board[i].above = (board[i + 4], None)
                else:
                    board[i].above = (None, None)
                board[i].below = (board[i - 4], None)
            else:
                if i % 8 in (0,1,2):
                    board[i].above = (board[i+5], board[i+4])
                    if i > 3:
                        board[i].below = (board[i-3], board[i-4])
                    else:
                        board[i].below = (None, None)
                elif i %8 in (5,6,7):
                    if i < 28:
                        board[i].above = (board[i+4], board[i+3])
                    else:
                        board[i].above = (None, None)
                    board[i].below = (board[i-4], board[i-5])

        self.board = board
        self.initial_turn = turn
        self.turn = turn
        self.moves_played = 0
        self.over = False
        self.winner = None
    
    def clone(self):
        cln = Game()
        for i in range(len(cln.board)):
            if not self.board[i].piece:
                cln.board[i].piece = None
            else:
                cln.board[i].piece = Piece(self.board[i].piece.colour)
                cln.board[i].piece.king = self.board[i].piece.king
        cln.initial_turn = self.initial_turn
        cln.turn = self.turn
        cln.moves_played = self.moves_played
        cln.over = self.over
        cln.winner = self.winner

    
    def outcome(self):
        if self.winner == None:
            return None
        if self.winner == self.initial_turn:
            return True
        else:
            return False
    
    def get_playable_moves(self):
        jumps = []
        moves = []
        for c in self.board:
            if c.piece and c.piece.colour == self.turn:
                jumps += c.valid_jumps()
                moves += c.valid_moves()
        return jumps if jumps else moves
    
    def do_move(self, move):
        self.board[move[0]].do_move(move[1])
        self.turn = 'black' if self.turn == 'white' else 'white'
        self.moves_played += 1
        if not self.get_playable_moves():
            self.over = True
            self.winner = 'black' if self.turn == 'white' else 'white'
    
    def random_move(self):
        return random.choice(self.get_playable_moves())

    def do_random_move(self):
        self.do_move(self.random_move())

    
    def __str__(self):
        s = ''
        for c in self.board:
            if c.piece:
                s += str(c.piece)
            else:
                s += 'x'
        return f"{self.turn[0]}+{s}"
    
    def __repr__(self):
        s = ''
        for i in range(31, -1, -1):
            if i % 8 <= 3:
                s += str(self.board[i]) + '[ ]'
            else:
                s += '[ ]' + str(self.board[i])

            if i % 4 == 0:
                s += '\n'
        return s
    

    @staticmethod
    def approximator(prev, new):
        # Extract voting coefficients from two sets of state/move pairs
        if prev[0][0] != new[0][0]:
            return
        for nmove in new[1]:
            for pmove in prev[1]:
                if pmove[1] != 0:
                    coeff = Game.mcompare(prev[0][2:], pmove[0], new[0][2:], nmove[0])
                    if coeff:
                        nmove[1][0] += coeff * pmove[1]
                        nmove[1][1] += 1

    @staticmethod
    def mcompare(pg, pm, ng, nm):
        def lists_are_equal(l1, l2):
            for a, b in zip(l1, l2):
                if isinstance(a, Iterable) and isinstance(b, Iterable):
                    if not lists_are_equal(a, b):
                        return False
                else:
                    if a != b:
                        return False
            return True
        ntog = lambda n : ((-(n%4) + 3)*2 + ((n//4) % 2), n // 4)
        gton = lambda g : 4*g[1] - (g[0] //2) + 3
        ghasval = lambda g : (g[0] + g[1]) % 2 == 0
        if not isinstance(pm[1], int) or not isinstance(nm[1], int):
            if isinstance(pm[1], int) or isinstance(nm[1], int):
                return False
            if len(pm[1]) != len(nm[1]):
                return False
            for i in range(len(pm[1])):
                if pg[pm[1][i][0]] != ng[nm[1][i][0]]:
                    return False
            pm = [pm[0]] + [m[1] for m in pm[1]]
            nm = [nm[0]] + [m[1] for m in nm[1]]

        pmn = [ntog(n) for n in pm]
        nmn = [ntog(n) for n in nm]
        diff = [pmn[0][0] - nmn[0][0], pmn[0][1] - nmn[0][1]]
        nmnd = [(m[0] + diff[0], m[1] + diff[1]) for m in nmn]
        if lists_are_equal(pmn, nmnd):
            similar_cells = 0
            if diff[0] < 0:
                nrangex = (0, 7 + diff[0])
            else:
                nrangex = (diff[0], 7)

            if diff[1] < 0:
                nrangey = (0, 7 + diff[1])
            else:
                nrangey = (diff[1], 7)

            nrange = (nrangex, nrangey)
            for i in range(nrange[0][0], nrange[0][1] + 1):
                for j in range(nrange[1][0], nrange[1][1] + 1):
                    if ghasval((i, j)):
                        if ng[gton((i, j))] == pg[gton((i - diff[0], j - diff[1]))]:
                            similar_cells += 1
                    else:
                        similar_cells += 1
            return similar_cells / 64

if __name__ == '__main__':
    game = Game()
    while not game.over:
        game.do_random_move()
        print(game.__repr__())
    print(game.winner)
