import pygame
from board import *
class Ai():
    def __init__(self, graphics, board):
        self.graphics = graphics
        self.board = board

    def dirs(self):
        return [NORTH, EAST, SOUTH, WEST]

    def rel(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx, y + dy

    def rel2(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx * 2, y + dy * 2

    def steps(self, pos):
        result = []
        for dir in self.dirs():
            dest = self.rel(pos, dir)
            if self.board.on_board(dest):
                result.append(dir)
        return result

    def legal_steps(self, pos):
        result = []
        for dir in self.steps(pos):
            dest = self.rel(pos, dir)
            if self.board.location(dest).occupant is None:
                result.append(dir)
        return result

    def hops(self, pos):
        result = []
        for dir in self.steps(pos):
            step = self.rel(pos, dir)
            hop = self.rel2(pos, dir)
            if self.board.on_board(hop) and self.board.location(hop).occupant is None and self.board.location(step).occupant is not None:
                result.append(dir)
        return result


    def build_rec(self, pos, travelled):
        best_score = None
        best_result = []
        hops = self.hops(pos)
        if len(hops) == 0:
            return []
        for hop in hops:
            x,y = self.rel2(pos, hop)
            if not travelled[x][y]:
                travelled[x][y] = True
                current_result = [hop]
                current_result += self.build_rec((x, y), travelled)
                travelled[x][y] = False
                score = self.evaluate(current_result)
                if best_score is None:
                    best_score = score
                    best_result = current_result

        return best_result

    def evaluate(self, path):
        return len(path)





    def calculate_best_legal_hop(self, pos):
        travelled = [[False] * 8 for i in range(8)]
        x,y = pos
        travelled[x][y] = True
        return self.build_rec(pos, travelled)

    def turn_magenta(self):
        best = []
        start = None
        best_score = None
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece is not None and piece.color == MAGENTA:
                    moves = self.board.legal_moves((x, y))
                    if len(moves) > 0:
                        current = self.calculate_best_legal_hop((x, y))
                        if best_score is None or self.evaluate(current) > best_score:
                            start = (x, y)
                            best = current
                            best_score = self.evaluate(current)
        if best_score > 0:
            piece = start
            for hop in best:
                dest = self.rel2(piece, hop)
                print("AI: piece jump ", piece, ' dest ', dest)
                self.board.move_piece(piece, dest)
                piece = dest
                self.graphics.screen.blit(self.graphics.background, (0, 0))
                self.graphics.draw_board_pieces(self.board)
                pygame.display.update()
                pygame.time.delay(500)
        else:

            move = None
            for x in range(8):
                for y in range(8):
                    piece = self.board.location((x, y)).occupant
                    if piece is not None and piece.color == MAGENTA:
                        moves = self.legal_steps((x, y))
                        if len(moves) > 0:
                            start = (x, y)
                            move = moves[0]
            if move is not None:
                dest = self.rel(start, move)
                print("AI: piece step ", start, ' dest ', dest)
                self.board.move_piece(start, dest)
                self.graphics.screen.blit(self.graphics.background, (0, 0))
                self.graphics.draw_board_pieces(self.board)
                pygame.display.update()
            else:
                print("Error, no AI MOVE FOUND")





        pass

    def turn_green(self):
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece != None and piece.color == GREEN:
                    pass

        #print('turn green ai')
        pass