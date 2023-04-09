import pygame
from board import *
class Ai():
    def __init__(self, graphics, board):
        self.empty_middle = None
        self.last_mode = None
        self.last_line = None
        self.turn = 1
        self.graphics = graphics
        self.board = board
        self.magenta = False
        self.opponent_help_anti_bonus = -60
        self.print_wm = False

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
                    #print("Best score: ", score, " result: ", pos, current_result)
                    best_score = score
                    best_result = current_result

        return best_result

    def at_home(self, pos):
        x,y = pos
        ##print("x >= 4", (x >= 4), "self.magenta", self.magenta, "y < 4", y < 4, " m==y<4", (self.magenta == (y < 4)))

        return x >= 4 and (self.magenta == (y < 4))

    def at_dest(self, pos):
        x,y = pos
        return x >= 4 and (self.magenta == (y >= 4))

    def manhatten(self, ax, ay, bx, by):
        return abs(bx - ax) + abs(by - ay)

    def manhetten(self, start, finish):
        sx, sy = start
        fx, fy = finish
        return max(0, 4 - max(abs(sy - fy), abs(sx - fx)))

    def worth_moving(self, start, finish, opponent):
        if self.turn > 50:
            self.print_wm = True
        sx, sy = start
        fx, fy = finish
        val = self.magenta != opponent
        
        em = self.empty_middle
        
        sign = 1 if val else -1
        horizontal_pull = fx - sx if (fy > 4) == val else 0
        vertical_pull = (fy - sy) * sign if not self.last_mode else 0 #4 - abs(fy - empty_middle)
        homestart = self.manhetten(start, (7, 0) if val else (7, 7))
        homefinish = self.manhetten(finish, (7, 0) if val else (7, 7))
        deststart = self.manhetten(start, (7, 7) if val else (7, 0))
        destfinish = self.manhetten(finish, (7, 7) if val else (7, 0))
        delta = self.manhatten(sx, sy, 4, em) - self.manhatten(fx, fy, 4, em)
        pull = vertical_pull + horizontal_pull + delta if deststart == 0 else 0

        if self.print_wm:
            print(
                'wm: vp ', vertical_pull, ' hp ', horizontal_pull, ' hs-hf ', (homestart - homefinish), ' d ', delta,
                ' df-ds ',  destfinish - deststart, ' fy-sy ', (fy-sy), ' fy-sy * sign ', (fy - sy) * sign,
                ' em ', em, ' fy - empty_middle ', fy - em, ' 4-|em| ', 4 - abs(fy - em),
                ' hs ', homestart, ' hf ', -homefinish, ' df ', destfinish, ' ds ', deststart)
        return pull + self.turn * (homestart - homefinish) + destfinish - deststart

    # def distance(self, start, finish):
    #     """ not a distance anymore"""
    #     sx, sy = start
    #     fx, fy = finish
    #     sign = 1 if self.magenta else -1
    #     homestart = self.manhetten(start, (7, 0) if self.magenta else (7, 7))
    #     homefinish = self.manhetten(finish, (7, 0) if self.magenta else (7, 7))
    #     deststart = self.manhetten(finish, (7, 7) if self.magenta else (7, 0))
    #     destfinish = self.manhetten(finish, (7, 7) if self.magenta else (7, 0))
    #     return (fy - sy) * sign + homestart - homefinish + destfinish - deststart

    def end(self, pos, path):
        end = pos
        for hop in path:
            end = self.rel2(end, hop)
        return end

    def score(self, h, x, y, pos):
        score = 0
        for item in h[x][y]:
            p, s, d, w = item
            if p != pos:
                score += s
        return score
    def evaluate(self, pos, path, helpers, opponent_helpers):
        if len(path) == 0:
            return 0
        start = pos
        end = pos

        color = MAGENTA if self.magenta else GREEN
        opponent_pieces = 0
        for hop in path:
            bridge = self.rel(end, hop)
            if self.board.location(bridge).occupant.color != color:
                opponent_pieces += 1
            end = self.rel2(end, hop)

        #print('evaluate hop pos', pos, ' path: ', path, ' end: ', end)

        bonus = 0
        """if self.at_dest(end):
            bonus += 60
        if self.at_home(start):
            bonus += 40
        if self.at_home(end):
            bonus -= 60"""

        sx, sy = start
        ex, ey = end

        add_score = self.score(helpers['add'], ex, ey, pos)

        if not self.last_mode:
            bonus += 20 * add_score

        #print('Add helpers: ', score)
        #print('bonus for add helper: ', 20 * score)
        #print('Rem helpers: ', helpers['rem'][sx][sy]);
        #print('bonus for rem helper: ', 20 * helpers['rem'][sx][sy]);

        rem_score = self.score(helpers['rem'], sx, sy, end)
        bonus += 20 * rem_score

        opp_add_score = self.score(opponent_helpers['add'], ex, ey, None)

        #print('Opponent Add helpers: ', score)
        #print('negative bonus for opp add helper: ', 20 * score)
        #print('Opponent Rem helpers: ', opponent_helpers['rem'][sx][sy]);
        #print('negative bonus for opp rem helper: ', 20 * opponent_helpers['rem'][sx][sy]);
        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_add_score

        opp_rem_score = self.score(opponent_helpers['rem'], sx, sy, end)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_rem_score

        e = self.worth_moving(start, end, False)
        fe = (20 + 25 * opponent_pieces) * e + bonus
        return [fe, e, opponent_pieces, self.turn, add_score, rem_score, opp_add_score, opp_rem_score]

    """if len(path) > 0:
        #print("self.magenta", self.magenta, " m==y<4", (self.magenta == (start[1] < 4)), "start", start, "end", end,
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

        #print('evaluateStep pos', pos, ' dir: ', dir)
        bonus = 0
        """if self.at_dest(end):
            #print('giving +60 bonus for reaching destination')
            bonus += 60
        if self.at_home(start):
            #print('giving +40 bonus for leaving home base')
            bonus += 40
        if self.at_home(end):
            #print('removing -60 bonus for staying or returning to home base')
            bonus -= 60"""

        sx, sy = start
        ex, ey = end

        add_score = self.score(helpers['add'], ex, ey, pos)

        #print('Add helpers: ', score)
        #print('bonus for add helper: ', 20 * score)
        if not self.last_mode:
            bonus += 20 * add_score
        #print('Rem helpers: ', helpers['rem'][sx][sy]);
        #print('bonus for rem helper: ', 20 * helpers['rem'][sx][sy]);
        rem_score = self.score(helpers['rem'], sx, sy, end)
        bonus += 20 * rem_score
        #print("Dir: ", dir, ' di: ', self.dirs().index(dir))
        #print('step helpers: ', helpers['step'][sx][sy][self.dirs().index(dir)]);
        #print('bonus for step helper: ', helpers['step'][sx][sy][self.dirs().index(dir)]);

        bonus += helpers['step'][sx][sy][self.dirs().index(dir)]

        opp_add_score = self.score(opponent_helpers['add'], ex, ey, None)

        ##print('Opponent Add helpers: ', score)
        ##print('negative bonus for opp add helper: ', 20 * score)
        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_add_score
        ##print('Opponent Rem helpers: ', opponent_helpers['rem'][sx][sy]);
        ##print('negative bonus for opp rem helper: ', 20 * opponent_helpers['rem'][sx][sy]);
        opp_rem_score = self.score(opponent_helpers['rem'], sx, sy, end)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_rem_score

        e = self.worth_moving(start, end, False)
        fe = 10 * e + bonus
        return [fe, e, self.turn, add_score, rem_score, opp_add_score, opp_rem_score]


    def d(self, dir):
        return 'N' if dir == NORTH else 'E' if dir == EAST else 'W' if dir == WEST else 'S'
    def print_h(self, ha):
        for j in range(8):
            x = ''
            for i in range(8):
                items = ha[i][j]
                if len(items) == 0:
                    x += '- '

                x += ' |'
                for item in ha[i][j]:
                    p, s, d, w = item
                    x += str(s) + self.d(d) + str(w) + ' '
                x += '| '
            print(x)

    def hopsHelpers(self, pos, path, travelled, helpers_add, helpers_step, opponent):
        result = []
        potential_blockers_to_remove = []
        for dir in self.steps(pos):
            step = self.rel(pos, dir)
            hop = self.rel2(pos, dir)
            hx, hy = hop
            #print('pos: ', pos, ' hop: ', hop, ' dir ', dir, 'on board? ', self.board.on_board(hop))
            #if self.board.on_board(hop):
                #print(' tr? ', travelled[hx][hy])
            if self.board.on_board(hop) and not travelled[hx][hy]:
                step_piece = self.board.location(step).occupant
                hop_piece = self.board.location(hop).occupant
                #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' sp ', step_piece)

                if hop_piece is None and step_piece is not None:
                    #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' adding result, before ', result)
                    result.append(dir)
                    #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' adding result, after ', result)

                elif hop_piece is not None and step_piece is not None:

                    #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' worth_moving ', self.worth_moving(pos, hop, magenta))
                    w = self.worth_moving(pos, hop, opponent)

                    if w > 0:
                        s, way = path
                        first = pos
                        if len(way) > 0:
                            first = self.rel2(s, way[0])

                        #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' potential_blockers_to_remove before ', potential_blockers_to_remove)
                        potential_blockers_to_remove.append([first, hop, dir, w])
                        #print('pos: ', pos, ' hop: ', hop, ' hp ', hop_piece, ' potential_blockers_to_remove after ', potential_blockers_to_remove)

                        #helpers_rem[hx][hy] += 1
                    if (hop_piece.color == MAGENTA) == self.magenta:
                        di = 0
                        for dir2 in self.steps(hop):
                            step2 = self.rel(hop, dir2)
                            hop2 = self.rel2(hop, dir2)
                            if hop2 != pos and self.board.on_board(hop2):
                                step_piece2 = self.board.location(step2).occupant
                                hop_piece2 = self.board.location(hop2).occupant
                                if self.worth_moving(pos, hop2, opponent) > 0:
                                    if hop_piece2 is None and step_piece2 is None:
                                        helpers_step[hx][hy][di] += 1
                            di += 1

                elif hop_piece is None and step_piece is None:
                    #print('Hop Helpers; pos: ', pos, ' step: ', step, ' hop: ', hop, ' dist: ', self.distance(pos, hop))
                    sx, sy = step
                    w = self.worth_moving(pos, hop, opponent)
                    #print('Hop Helpers; pos: ', pos, ' step: ', step, ' hop: ', hop, ' w: ', w)
                    if w > 0:
                        helpers_add[sx][sy].append([pos, 1, dir, w])

        return [result, potential_blockers_to_remove]


    def traverse(self, pos, path, travelled, helpers_add, helpers_rem, helpers_step, opponent):
        #print('Helpers Traverse Enter. m: ', magenta, ' pos ', pos, ' tr ', travelled)
        hops, blockers = self.hopsHelpers(pos, path, travelled, helpers_add, helpers_step, opponent)
        if len(hops) == 0:
            return [[path, blockers]]
        results = [[path, blockers]] if opponent else []
        for hop in hops:
            x,y = self.rel2(pos, hop)
            if not travelled[x][y]:
                travelled[x][y] = True
                start, way = path
                way = way.copy()
                way.append(hop)
                results += self.traverse((x, y), [start, way], travelled, helpers_add, helpers_rem, helpers_step, opponent)
                travelled[x][y] = False
        return results

    def helpers(self, opponent):
        helpers_add = [[[] for i in range(8)] for i in range(8)]
        helpers_rem = [[[] for i in range(8)] for i in range(8)]
        helpers_step = [[[0] * 4 for i in range(8)] * 8 for i in range(8)]

        hops = []
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece is not None and (((piece.color == MAGENTA) == self.magenta) != opponent):
                    #print('Helpers Traverse start. m: ', magenta, ' pc ', piece.color, ' x y ', x, y)
                    travelled = [[False] * 8 for i in range(8)]
                    travelled[x][y] = True
                    path = [(x, y), []]
                    results = self.traverse((x, y), path, travelled, helpers_add, helpers_rem, helpers_step, opponent)
                    hops.append([(x, y), results])
                    if len(results) == 1 or opponent:
                        for result in results:
                            p, b = result
                            s, w = p

                            for (pos, hop, dir, w) in b:
                                hx, hy = hop
                                #print('s: ', s, ' hop: ', hop, ' adding to rem helper since len(results) = 1 ', len(results))
                                helpers_rem[hx][hy].append([pos, 1, dir, w])

        return {'add': helpers_add, 'rem': helpers_rem, 'step': helpers_step, 'hops': hops}







    # def calculate_best_legal_hop(self, pos, helpers, opponent_helpers):
    #     travelled = [[False] * 8 for i in range(8)]
    #     x,y = pos
    #     travelled[x][y] = True
    #     return self.build_rec(pos, travelled, helpers, opponent_helpers)
    #
    # def find_best_move_for_piece(self, pos, helpers, opponent_helpers):
    #     best = None
    #     bestIsHop = None
    #     bestStepDir = None
    #     current = []
    #     piece = self.board.location(pos).occupant
    #     if piece is not None and ((piece.color == MAGENTA) == self.magenta):
    #         current = self.calculate_best_legal_hop(pos, helpers, opponent_helpers)
    #         best, other = self.evaluate(pos, current, helpers, opponent_helpers)
    #         bestIsHop = True
    #
    #         moves = self.legal_steps(pos)
    #         for move in moves:
    #             score = self.evaluateStep(pos, move, helpers, opponent_helpers)
    #             if best is None or score > best:
    #                 bestIsHop = False
    #                 bestStepDir = move
    #                 best = score
    #     #print("Overall Best score is : ", best, current if bestIsHop else bestStepDir)
    #     return [best, bestIsHop, current if bestIsHop else bestStepDir]

    def show_moves(self, start, is_hop, moves):
        piece = start
        if is_hop:
            for hop in moves:
                dest = self.rel2(piece, hop)
                #print("AI: piece jump ", piece, ' dest ', dest)
                self.board.move_piece(piece, dest)
                piece = dest
                self.graphics.screen.blit(self.graphics.background, (0, 0))
                self.graphics.draw_board_pieces(self.board)
                if self.graphics.message:
                    self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
                pygame.display.update()
                pygame.time.delay(500)
        else:
            dest = self.rel(start, moves)
            #print("AI: piece step ", start, ' dest ', dest)
            self.board.move_piece(start, dest)
            self.graphics.screen.blit(self.graphics.background, (0, 0))
            self.graphics.draw_board_pieces(self.board)
            if self.graphics.message:
                self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
            pygame.display.update()

    def last_green_line(self):
        last_completed_line = -1
        for y in range(4):
            for x in range(4, 8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is None or piece.color != GREEN:
                    return last_completed_line
            last_completed_line = y
        return last_completed_line

    def last_magenta_line(self):
        last_completed_line = 8
        for y in reversed(range(4, 8)):
            for x in range(4, 8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is None or piece.color != MAGENTA:
                    return last_completed_line
            last_completed_line = y
        return last_completed_line

    def turn_magenta(self, turn):
        self.magenta = True
        self.turn = turn
        best_is_hop = False
        best_move = None
        start = None
        best_score = None

        #print('MAGENTA TURN AI')

        self.last_line = self.last_magenta_line() if self.magenta else self.last_green_line()
        self.last_mode = self.last_line != -1 and self.last_line != 8
        self.empty_middle = (4 + self.last_line - 1) >> 1 if self.magenta else (3 + self.last_line + 1) >> 1

        helpers = self.helpers(False)
        opponent_helpers = self.helpers(True)
        print('SELF ADD')
        self.print_h(helpers['add'])
        print('SELF REM')
        self.print_h(helpers['rem'])
        print('OPP ADD')
        self.print_h(opponent_helpers['add'])
        print('OPP REM')
        self.print_h(opponent_helpers['rem'])



        hops = helpers['hops']
        for hop in hops:
            s, results = hop
            for result in results:
                p, b = result
                ss, p = p
                if len(p) > 0:
                    f = self.end(s, p)
                    w = self.worth_moving(s, f, False)
                    e, we, op, t, ads, rs, oas, ors = self.evaluate(s, p, helpers, opponent_helpers)
                    print(
                        'S: ', s, ' P: ', p, ' f: ', f, ' w: ', w, ' e: ', e, ' we ', we, ' op ', op, ' t ',  t,
                        ' as ', ads, ' rs ', rs, ' oas ', oas, ' ors ', ors
                    )
                    if best_score is None or e > best_score:
                        start = s
                        best_is_hop = True
                        best_move = p
                        best_score = e


        # for x in range(4, 8):
        #     for y in range(4):
        for x in range(8):
            for y in range(8):
                pos = (x, y)
                piece = self.board.location(pos).occupant
                if piece is not None and ((piece.color == MAGENTA) == self.magenta):
                    moves = self.legal_steps(pos)
                    for move in moves:
                        f = self.rel(pos, move)
                        score, we, t, ads, rs, oas, ors = self.evaluateStep(pos, move, helpers, opponent_helpers)
                        print(
                            'STEP S: ', pos, ' move: ', move, ' f: ', f,   ' e: ', score, ' we ', we, ' t ', t,
                            ' as ', ads, ' rs ', rs, ' oas ', oas, ' ors ', ors
                        )
                        if best_score is None or score > best_score:
                            start = pos
                            best_is_hop = False
                            best_move = move
                            best_score = score

        if best_score is not None:
            self.show_moves(start, best_is_hop, best_move)
        # else:
        #     for x in range(8):
        #         for y in range(8):
        #             score, is_hop, moves = self.find_best_move_for_piece((x, y), helpers, opponent_helpers)
        #             if score is not None and score > 0 and (best_score is None or score > best_score):
        #                 start = (x, y)
        #                 best_is_hop = is_hop
        #                 best_move = moves
        #                 best_score = score
        #                 #print("Overall Best score: ", score, " result: ", start, moves)
        #     if best_score > 0:
        #         self.show_moves(start, best_is_hop, best_move)





        pass

    def turn_green(self):
        self.magenta = False
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece != None and piece.color == GREEN:
                    pass

        ##print('turn green ai')
        pass