import pygame
from board import *
class ImprovedOldAi():
    def __init__(self, graphics, board):
        self.graphics = graphics
        self.board = board
        self.magenta = False

    def rel(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx, y + dy

    def rel2(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx * 2, y + dy * 2

    def turn_green(self):
        self.magenta = False
        start, dest = self.find_green()
        self.board.move_piece(start, dest)
        self.graphics.screen.blit(self.graphics.background, (0, 0))
        self.graphics.draw_board_pieces(self.board)
        if self.graphics.message:
            self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
        pygame.display.update()

    def turn_magenta(self):
        self.magenta = True
        start, dest = self.find_magenta()
        self.board.move_piece(start, dest)
        self.graphics.screen.blit(self.graphics.background, (0, 0))
        self.graphics.draw_board_pieces(self.board)
        if self.graphics.message:
            self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
        pygame.display.update()
    def find_green(self):
        for dir in [NORTH, WEST]:
            for y in reversed(range(4, 8)):
                for x in reversed(range(4, 8)):
                    start = (x, y)
                    piece = self.board.location(start).occupant
                    if piece is not None and piece.color == GREEN:
                        step = self.rel(start, dir)
                        hop = self.rel2(start, dir)
                        if self.board.on_board(hop):
                            sp = self.board.location(step).occupant
                            hp = self.board.location(hop).occupant
                            if sp is not None and hp is None:
                                print("Improved; s: ", start, ' h ', hop)
                                return [start, hop]
        for dir in [NORTH, WEST]:
            for y in reversed(range(4, 8)):
                for x in reversed(range(4, 8)):
                    start = (x, y)
                    piece = self.board.location(start).occupant
                    if piece is not None and piece.color == GREEN:
                        step = self.rel(start, dir)
                        if self.board.on_board(step):
                            sp = self.board.location(step).occupant
                            if sp is None:
                                print("Improved; s: ", start, ' st ', step)
                                return [start, step]
        print("All pieces moved out of the base???")
        for x in reversed(range(8)):
            for y in range(1, 8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, NORTH)
                    sp = self.board.location(step).occupant
                    if sp is None:
                        return [start, step]
                    if y > 1:
                        hop = self.rel2(start, NORTH)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]

        for x in range(7):
            for y in range(8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, EAST)
                    print('s: ', start, ' step: ', step)
                    sp = self.board.location(step).occupant
                    sx, sy = step
                    if sp is None and not (sx >= 4 and sy >= 4):
                        return [start, step]
                    if x < 6:
                        hop = self.rel2(start, EAST)
                        hp = self.board.location(hop).occupant
                        hx, hy = hop
                        if sp is not None and hp is None and not (hx >= 4 and hy >= 4):
                            return [start, hop]
        for x in range(1, 8):
            for y in range(8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, WEST)
                    sp = self.board.location(step).occupant
                    if sp is None:
                        return [start, step]
                    if x > 1:
                        hop = self.rel2(start, WEST)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]
        print("Error in OLD AI. Cannot find a move")

    def find_magenta(self):
        for x in reversed(range(8)):
            for y in range(7):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, SOUTH)
                    sp = self.board.location(step).occupant
                    if sp is None:
                        return [start, step]
                    if y < 6:
                        hop = self.rel2(start, SOUTH)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]

        for x in range(7):
            for y in range(8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, EAST)
                    sp = self.board.location(step).occupant
                    if sp is None:
                        return [start, step]
                    if x < 6:
                        hop = self.rel2(start, EAST)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]
        for x in range(1, 8):
            for y in reversed(range(8)):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, WEST)
                    sp = self.board.location(step).occupant
                    if sp is None:
                        return [start, step]
                    if x > 1:
                        hop = self.rel2(start, WEST)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]
        print("Error in OLD AI. Cannot find a move")
