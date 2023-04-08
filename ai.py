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


    def build_rec(self, pos, travelled, helpers, opponent_helpers):
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
                current_result += self.build_rec((x, y), travelled, helpers, opponent_helpers)
                travelled[x][y] = False
                score = self.evaluate(pos, current_result, helpers, opponent_helpers)
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

    def manhetten(self, start, finish):
        sx, sy = start
        fx, fy = finish
        return max(0, 4 - max(abs(sy - fy), abs(sx - fx)))

    def worth_moving(self, start, finish, magenta):
        sx, sy = start
        fx, fy = finish
        sign = 1 if magenta else -1
        homestart = self.manhetten(start, (7, 0) if magenta else (7, 7))
        homefinish = self.manhetten(finish, (7, 0) if magenta else (7, 7))
        deststart = self.manhetten(finish, (7, 7) if magenta else (7, 0))
        destfinish = self.manhetten(finish, (7, 7) if magenta else (7, 0))
        return (fy - sy) * sign + homestart - homefinish + destfinish - deststart

    def distance(self, start, finish):
        """ not a distance anymore"""
        sx, sy = start
        fx, fy = finish
        sign = 1 if self.magenta else -1
        homestart = self.manhetten(start, (7, 0) if self.magenta else (7, 7))
        homefinish = self.manhetten(finish, (7, 0) if self.magenta else (7, 7))
        deststart = self.manhetten(finish, (7, 7) if self.magenta else (7, 0))
        destfinish = self.manhetten(finish, (7, 7) if self.magenta else (7, 0))
        return (fy - sy) * sign + homestart - homefinish + destfinish - deststart

    def evaluate(self, pos, path, helpers, opponent_helpers):
        if len(path) == 0:
            return 0
        start = pos
        end = pos
        for hop in path:
            end = self.rel2(end, hop)

        print('evaluate hop pos', pos, ' path: ', path, ' end: ', end)

        bonus = 0
        """if self.at_dest(end):
            bonus += 60
        if self.at_home(start):
            bonus += 40
        if self.at_home(end):
            bonus -= 60"""

        sx, sy = start
        ex, ey = end


        score = 0
        for item in helpers['add'][ex][ey]:
            if item['pos'] != pos:
                score += item['score']

        print('Add helpers: ', score)
        print('bonus for add helper: ', 20 * score)
        print('Rem helpers: ', helpers['rem'][sx][sy]);
        print('bonus for rem helper: ', 20 * helpers['rem'][sx][sy]);
        bonus += 20 * score
        bonus += 20 * helpers['rem'][sx][sy]

        score = 0
        for item in opponent_helpers['add'][ex][ey]:
            score += item['score']
        print('Opponent Add helpers: ', score)
        print('negative bonus for opp add helper: ', 20 * score)
        print('Opponent Rem helpers: ', opponent_helpers['rem'][sx][sy]);
        print('negative bonus for opp rem helper: ', 20 * opponent_helpers['rem'][sx][sy]);
        bonus -= 20 * score
        bonus -= 20 * opponent_helpers['rem'][sx][sy]

        return self.distance(start, end) + bonus

    """if len(path) > 0:
        print("self.magenta", self.magenta, " m==y<4", (self.magenta == (start[1] < 4)), "start", start, "end", end,
              "ah?s ", self.at_home(start), " ad?e", self.at_dest(end), " ah?e ", self.at_home(end))
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
        return len(path)"""

    def evaluateStep(self, pos, dir, helpers, opponent_helpers):
        start = pos
        end = self.rel(pos, dir)

        print('evaluateStep pos', pos, ' dir: ', dir)
        bonus = 0
        """if self.at_dest(end):
            print('giving +60 bonus for reaching destination')
            bonus += 60
        if self.at_home(start):
            print('giving +40 bonus for leaving home base')
            bonus += 40
        if self.at_home(end):
            print('removing -60 bonus for staying or returning to home base')
            bonus -= 60"""

        sx, sy = start
        ex, ey = end

        score = 0
        for item in helpers['add'][ex][ey]:
            print('POS: ', pos, ' item.pos: ', item['pos'], ' score: ', item['score'])
            if item['pos'] != pos:
                score += item['score']

        print('Add helpers: ', score)
        print('bonus for add helper: ', 20 * score)

        bonus += 20 * score
        print('Rem helpers: ', helpers['rem'][sx][sy]);
        print('bonus for rem helper: ', 20 * helpers['rem'][sx][sy]);
        bonus += 20 * helpers['rem'][sx][sy]
        print("Dir: ", dir, ' di: ', self.dirs().index(dir))
        print('step helpers: ', helpers['step'][sx][sy][self.dirs().index(dir)]);
        print('bonus for step helper: ', helpers['step'][sx][sy][self.dirs().index(dir)]);

        bonus += helpers['step'][sx][sy][self.dirs().index(dir)]

        score = 0
        for item in opponent_helpers['add'][ex][ey]:
            score += item['score']

        print('Opponent Add helpers: ', score)
        print('negative bonus for opp add helper: ', 20 * score)

        bonus -= 20 * score
        print('Opponent Rem helpers: ', opponent_helpers['rem'][sx][sy]);
        print('negative bonus for opp rem helper: ', 20 * opponent_helpers['rem'][sx][sy]);

        bonus -= 20 * opponent_helpers['rem'][sx][sy]

        return self.distance(start, end) + bonus

    def print_h(self, ha):
        for i in range(8):
            for j in range(8):
                data = ha[i][j]
                if len(data) > 0:
                    for item in data:
                        print("i: ", i, " j: ", j, " ", " it.p: ", item['pos'], " it.s: ", item['score'])
    def print_hr(self, hr):
        for i in range(8):
            for j in range(8):
                if hr[i][j] > 0:
                    print("i: ", i, " j: ", j, " ", " hr: ", hr[i][j])

    def hopsHelpers(self, pos, helpers_add, helpers_rem, helpers_step, magenta):
        result = []
        potential_blockers_to_remove = []
        for dir in self.steps(pos):
            step = self.rel(pos, dir)
            hop = self.rel2(pos, dir)
            if self.board.on_board(hop):
                step_piece = self.board.location(step).occupant
                hop_piece = self.board.location(hop).occupant
                if hop_piece is None and step_piece is not None:
                    result.append(dir)
                elif hop_piece is not None and step_piece is not None:
                    hx, hy = hop

                    if self.worth_moving(pos, hop, magenta) > 0:
                        potential_blockers_to_remove.append(hop)
                        #helpers_rem[hx][hy] += 1
                    if (hop_piece.color == MAGENTA) == self.magenta:
                        di = 0
                        for dir2 in self.steps(hop):
                            step2 = self.rel(hop, dir2)
                            hop2 = self.rel2(hop, dir2)
                            if hop2 != pos and self.board.on_board(hop2):
                                step_piece2 = self.board.location(step2).occupant
                                hop_piece2 = self.board.location(hop2).occupant
                                if self.distance(pos, hop2) > 0:
                                    if hop_piece2 is None and step_piece2 is None:
                                        helpers_step[hx][hy][di] += 1
                            di += 1

                elif hop_piece is None and step_piece is None:
                    print('Hop Helpers; pos: ', pos, ' step: ', step, ' hop: ', hop, ' dist: ', self.distance(pos, hop))
                    sx, sy = step
                    if self.distance(pos, hop) > 0:
                        helpers_add[sx][sy].append({'pos':pos,'score':1})
        if len(result) == 0:
            for hop in potential_blockers_to_remove:
                hx, hy = hop
                print('pos: ', pos, ' hop: ', hop, ' adding to rem helper since len(res) ', len(result))
                helpers_rem[hx][hy] += 1

        return result


    def traverse(self, pos, travelled, helpers_add, helpers_rem, helpers_step, magenta):
        hops = self.hopsHelpers(pos, helpers_add, helpers_rem, helpers_step, magenta)
        if len(hops) == 0:
            return []
        for hop in hops:
            x,y = self.rel2(pos, hop)
            if not travelled[x][y]:
                travelled[x][y] = True
                self.traverse((x, y), travelled, helpers_add, helpers_rem, helpers_step, magenta)
                travelled[x][y] = False

    def helpers(self, magenta):
        helpers_add = [[[] for i in range(8)] for i in range(8)]
        helpers_rem = [[0] * 8 for i in range(8)]
        helpers_step = [[[0] * 4 for i in range(8)] * 8 for i in range(8)]

        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece is not None and ((piece.color == MAGENTA) == magenta):
                    print('Helpers Traverse start. m: ', magenta, ' pc ', piece.color, ' x y ', x, y)
                    travelled = [[False] * 8 for i in range(8)]
                    travelled[x][y] = True
                    self.traverse((x, y), travelled, helpers_add, helpers_rem, helpers_step, magenta)

        return {'add': helpers_add, 'rem': helpers_rem, 'step': helpers_step}







    def calculate_best_legal_hop(self, pos, helpers, opponent_helpers):
        travelled = [[False] * 8 for i in range(8)]
        x,y = pos
        travelled[x][y] = True
        return self.build_rec(pos, travelled, helpers, opponent_helpers)

    def turn_magenta(self):
        self.magenta = True
        bestIsHop = False
        bestHop = []
        bestStepDir = None
        start = None
        best_score = None

        print('MAGENTA TURN AI')


        helpers = self.helpers(self.magenta)
        opponent_helpers = self.helpers(not self.magenta)

        self.print_h(opponent_helpers['add'])
        self.print_hr(opponent_helpers['rem'])
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece is not None and piece.color == MAGENTA:
                    current = self.calculate_best_legal_hop((x, y), helpers, opponent_helpers)
                    score = self.evaluate((x, y), current, helpers, opponent_helpers)
                    if score > 0 and (best_score is None or score > best_score):
                        start = (x, y)
                        bestIsHop = True
                        bestHop = current
                        best_score = score
                        print("Overall Best score: ", score, " result: ", start, current)
                    moves = self.legal_steps((x, y))
                    for move in moves:
                        score = self.evaluateStep((x, y), move, helpers, opponent_helpers)
                        if best_score is None or score > best_score:
                            start = (x, y)
                            bestIsHop = False
                            bestStepDir = move
                            best_score = score
                            print("Overall Best score is step: ", score, " result: ", start, move)
        if best_score > 0:
            piece = start
            if bestIsHop:
                for hop in bestHop:
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
                dest = self.rel(start, bestStepDir)
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