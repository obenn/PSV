class Piece:
    def __init__(self, colour):
        self.colour = colour
        self.king = False
        self.dead = False
    
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
                        if self.above[i].above[i] not in exclude:
                            jumps.append((self.above[i], self.above[i].above[i]))
        if colour == 'white' or king:
            for i in (0, 1):
                if self.below[i] and self.below[i].piece and self.below[i].piece.colour != colour:
                    if self.below[i].below[i] and self.below[i].below[i].piece == None:
                        if self.below[i].below[i] not in exclude:
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
        # TODO: RECURSIVE FOR ALL ACTUAL JUMPS
        #return [(self.index, ((s.index, d.index),)) for s, d in self.possible_jumps(self.piece.colour, self.piece.king)]
        jump_paths = [[j] for j in self.possible_jumps(self.piece.colour, self.piece.king)]
        done = False
        while not done:
            jump_paths_new = []
            for path in jump_paths:
                npaths = path[-1][1].possible_jumps(self.piece.colour, self.piece.king, exclude=[p[1] for p in path])
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
                c.piece.dead = True
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

        self.black_pieces = [Piece('black') for _ in range(12)]
        self.white_pieces = [Piece('white') for _ in range(12)]

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
        import random
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
        return f"{self.turn}+{s}"
    
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

if __name__ == '__main__':
    game = Game()
    while not game.over:
        game.do_random_move()
        print(game.__repr__())
    print(game.winner)
