import pygame
from board import *
class Ai():
    def __init__(self, graphics, board):
        self.graphics = graphics
        self.board = board
        self.magenta = False

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
                score = self.evaluate(pos, current_result)
                if best_score is None:
                    print("Best score: ", score, " result: ", pos, current_result)
                    best_score = score
                    best_result = current_result

        return best_result

    def at_home(self, pos):
        x,y = pos
        #print("x >= 4", (x >= 4), "self.magenta", self.magenta, "y < 4", y < 4, " m==y<4", (self.magenta == (y < 4)))

        return x >= 4 and (self.magenta == (y < 4))

    def at_dest(self, pos):
        x,y = pos
        return x >= 4 and (self.magenta == (y >= 4))

    def evaluate(self, pos, path):
        start = pos
        end = pos
        for hop in path:
            end = self.rel2(end, hop)

        if len(path) > 0:
            print("self.magenta", self.magenta, " m==y<4", (self.magenta == (start[1] < 4)),  "start", start, "end", end, "ah?s ", self.at_home(start), " ad?e", self.at_dest(end), " ah?e ", self.at_home(end))
        if self.at_home(start) and self.at_dest(end):
            return 100 * len(path)
        elif self.at_home(end):
            return 0
        elif not self.at_home(start) and not self.at_dest(start) and self.at_dest(end):
            return 50 * len(path)
        elif self.at_home(start) and not self.at_home(end):
            return 20 * len(path)
        elif not self.at_dest(start) and not self.at_home(end):
            return 10 * len(path)
        else:
            return len(path)





    def calculate_best_legal_hop(self, pos):
        travelled = [[False] * 8 for i in range(8)]
        x,y = pos
        travelled[x][y] = True
        return self.build_rec(pos, travelled)

    def turn_magenta(self):
        self.magenta = True
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
                        score = self.evaluate((x, y), current)
                        if best_score is None or score > best_score:

                            start = (x, y)
                            best = current
                            best_score = score
                            print("Overall Best score: ", score, " result: ", start, current)
        if best_score > 0:
            piece = start
            for hop in best:
                dest = self.rel2(piece, hop)
                print("AI: piece jump ", piece, ' dest ', dest)
                self.board.move_piece(piece, dest)
                piece = dest
                self.graphics.screen.blit(self.graphics.background, (0, 0))
                self.graphics.draw_board_pieces(self.board)
                if self.graphics.message:
                    self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
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
                if self.graphics.message:
                    self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
                pygame.display.update()
            else:
                print("Error, no AI MOVE FOUND")





        pass

    def turn_green(self):
        self.magenta = False
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece != None and piece.color == GREEN:
                    pass

        #print('turn green ai')
        pass