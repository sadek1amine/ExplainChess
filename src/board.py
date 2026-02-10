from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Board:

    def __init__(self):
        self.squares = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    # ------------------ BOARD SETUP ------------------
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))

    # ------------------ MOVE PIECES ------------------
    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # move the piece
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # pawn specific
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:  # en passant
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            else:  # promotion
                self.check_promotion(piece, final)

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if diff < 0 else piece.right_rook
                self.move(rook, rook.moves[-1])

        piece.moved = True
        piece.clear_moves()
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return
        for row in range(ROWS):
            for col in range(COLS):
                p = self.squares[row][col].piece
                if isinstance(p, Pawn):
                    p.en_passant = False
        piece.en_passant = True

    # ------------------ CHECK DETECTION ------------------
    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    # ------------------ CALCULATE MOVES ------------------
    def calc_moves(self, piece, row, col, bool=True):
        piece.clear_moves()

        # ---------- PAWN ----------
        def pawn_moves():
            direction = piece.dir
            start_row = row + direction

            # one step forward
            if Square.in_range(start_row) and self.squares[start_row][col].isempty():
                move = Move(Square(row, col), Square(start_row, col))
                if not bool or not self.in_check(piece, move):
                    piece.add_move(move)

                # two steps forward
                if not piece.moved:
                    two_step = start_row + direction
                    if Square.in_range(two_step) and self.squares[two_step][col].isempty():
                        move = Move(Square(row, col), Square(two_step, col))
                        if not bool or not self.in_check(piece, move):
                            piece.add_move(move)

            # diagonal captures
            for dc in [-1, 1]:
                r = row + direction
                c = col + dc
                if Square.in_range(r, c):
                    if self.squares[r][c].has_enemy_piece(piece.color):
                        final_piece = self.squares[r][c].piece
                        move = Move(Square(row, col), Square(r, c, final_piece))
                        if not bool or not self.in_check(piece, move):
                            piece.add_move(move)

            # en passant
            ep_row = 3 if piece.color == 'white' else 4
            final_row = 2 if piece.color == 'white' else 5
            if row == ep_row:
                for dc in [-1, 1]:
                    c = col + dc
                    if Square.in_range(c):
                        p = self.squares[row][c].piece
                        if isinstance(p, Pawn) and p.en_passant:
                            move = Move(Square(row, col), Square(final_row, c, p))
                            if not bool or not self.in_check(piece, move):
                                piece.add_move(move)

        # ---------- KNIGHT ----------
        def knight_moves():
            moves = [
                (row-2, col+1), (row-1, col+2),
                (row+1, col+2), (row+2, col+1),
                (row+2, col-1), (row+1, col-2),
                (row-1, col-2), (row-2, col-1),
            ]
            for r, c in moves:
                if Square.in_range(r, c) and self.squares[r][c].isempty_or_enemy(piece.color):
                    final_piece = self.squares[r][c].piece
                    move = Move(Square(row, col), Square(r, c, final_piece))
                    if not bool or not self.in_check(piece, move):
                        piece.add_move(move)

        # ---------- SLIDING PIECES ----------
        def straightline_moves(directions):
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while Square.in_range(r, c):
                    final_piece = self.squares[r][c].piece
                    move = Move(Square(row, col), Square(r, c, final_piece))

                    if self.squares[r][c].isempty():
                        if not bool or not self.in_check(piece, move):
                            piece.add_move(move)
                    elif self.squares[r][c].has_enemy_piece(piece.color):
                        if not bool or not self.in_check(piece, move):
                            piece.add_move(move)
                        break
                    else:
                        break
                    r += dr
                    c += dc

        # ---------- KING ----------
        def king_moves():
            adjs = [
                (row-1, col), (row-1, col+1), (row, col+1), (row+1, col+1),
                (row+1, col), (row+1, col-1), (row, col-1), (row-1, col-1)
            ]
            for r, c in adjs:
                if Square.in_range(r, c) and self.squares[r][c].isempty_or_enemy(piece.color):
                    final_piece = self.squares[r][c].piece
                    move = Move(Square(row, col), Square(r, c, final_piece))
                    if not bool or not self.in_check(piece, move):
                        piece.add_move(move)

        # ---------- DISPATCH ----------
        if isinstance(piece, Pawn):
            pawn_moves()
        elif isinstance(piece, Knight):
            knight_moves()
        elif isinstance(piece, Bishop):
            straightline_moves([(-1,1), (-1,-1), (1,1), (1,-1)])
        elif isinstance(piece, Rook):
            straightline_moves([(-1,0), (0,1), (1,0), (0,-1)])
        elif isinstance(piece, Queen):
            straightline_moves([
                (-1,1), (-1,-1), (1,1), (1,-1),
                (-1,0), (0,1), (1,0), (0,-1)
            ])
        elif isinstance(piece, King):
            king_moves()




        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create new move
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                            else: break
                        else:
                            # append new move
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create squares of the possible new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create a possible new move
                        move = Move(initial, final)

                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

                        # has enemy piece = add move + break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
                            break

                        # has team piece = break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    
                    # not in range
                    else: break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0), # up
                (row-1, col+1), # up-right
                (row+0, col+1), # right
                (row+1, col+1), # down-right
                (row+1, col+0), # down
                (row+1, col-1), # down-left
                (row+0, col-1), # left
                (row-1, col-1), # up-left
            ]

            # normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) # piece=piece
                        # create new move
                        move = Move(initial, final)
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                            else: break
                        else:
                            # append new move
                            piece.add_move(move)

            # castling moves
            if not piece.moved:
                # queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3:
                                # adds left rook to king
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                # check potencial checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        # append new move to rook
                                        left_rook.add_move(moveR)
                                        # append new move to king
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook
                                    left_rook.add_move(moveR)
                                    # append new move king
                                    piece.add_move(moveK)

                # king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6:
                                # adds right rook to king
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                # check potencial checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        # append new move to rook
                                        right_rook.add_move(moveR)
                                        # append new move to king
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook
                                    right_rook.add_move(moveR)
                                    # append new move king
                                    piece.add_move(moveK)

        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1), # down-left
            ])

        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0), # up
                (0, 1), # right
                (1, 0), # down
                (0, -1), # left
            ])

        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1), # down-left
                (-1, 0), # up
                (0, 1), # right
                (1, 0), # down
                (0, -1) # left
            ])

        elif isinstance(piece, King): 
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))