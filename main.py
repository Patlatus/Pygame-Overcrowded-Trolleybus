"""
Loosely based upon https://github.com/quyq/Pygame-Checkers
However, here a completely different game is built while still on chessboard.
Colors of the board cells and pieces were changed to match the original game implemented in Delphi
"""
import pygame, sys
from pygame.locals import *
from enum import Enum
from graphics import Graphics
from board import *
from button import Button
from ai import Ai
from old_ai import OldAi
from improved_old_ai import ImprovedOldAi

pygame.font.init()


class Level(Enum):
	OLD = 0
	OLD_IMP = 1
	NEW = 2


class Game:
	"""
	The main game control.
	"""

	run = True

	def __init__(self):
		self.green = 1
		self.magenta = 1
		self.end = False
		self.graphics = Graphics()
		self.board = Board()
		self.ai = Ai(self.graphics, self.board)
		self.oldai = OldAi(self.graphics, self.board)
		self.impoldai = ImprovedOldAi(self.graphics, self.board)
		self.level = Level.NEW
		
		self.turn = GREEN
		self.selected_piece = None # a board location. 
		self.hop = False
		self.selected_legal_moves = []

		self.TICK = pygame.USEREVENT
		self.AI_TICK = pygame.USEREVENT + 1
		pygame.time.set_timer(self.TICK, 500)
		pygame.time.set_timer(self.AI_TICK, 1200)
		self.show_menu = False
		self.show_main_menu = False
		self.show_options = False
		self.show_level = False
		self.ai_green = False
		self.ai_magenta = False
		self.delay_ai = False

		self.play_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 6),
								  text_input="RESUME GAME", font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		self.restart_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								  text_input="RESTART GAME", font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		# pygame.image.load("assets/Options Rect.png")
		self.options_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 6),
									 text_input="OPTIONS", font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		self.level_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
									 text_input="AI Level", font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		# pygame.image.load("assets/Quit Rect.png")
		self.quit_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 6 // 6),
								  text_input="QUIT", font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")

		self.human_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 6),
								  text_input="HUMAN VS HUMAN", font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		self.ai_starts = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								  text_input="AI VS HUMAN", font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		# pygame.image.load("assets/Options Rect.png")
		self.ai_strikes_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 6),
									 text_input="HUMAN VS AI", font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		self.options_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
							  text_input="BACK", font=self.get_font(75), base_color="#d7fcd4",
							  hovering_color="White")

		self.old_ai_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 6),
								   text_input="Old AI (2003): Primitive", font=self.get_font(75), base_color="#d7fcd4",
								   hovering_color="White")
		self.imp_old_ai_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								text_input="Improved Old AI: Easy", font=self.get_font(75), base_color="#d7fcd4",
								hovering_color="White")
		# pygame.image.load("assets/Options Rect.png")
		self.new_ai_choice = Button(image=None,
									  pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 6),
									  text_input="New AI (2023): Medium", font=self.get_font(75), base_color="#d7fcd4",
									  hovering_color="White")
		self.level_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
								   text_input="BACK", font=self.get_font(75), base_color="#d7fcd4",
								   hovering_color="White")

	def setup(self):
		"""Draws the window and board at the beginning of the game"""
		self.graphics.setup_window()

	def get_font(self, size):
		return pygame.font.SysFont("comicsans", 40)  # pygame.font.Font("assets/font.ttf", size)

	def process_main_menu(self, mouse_pos):
		if self.play_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_menu = False
			if not self.is_human_turn():
				self.perform_ai_turn()
		if self.restart_button.checkForInput(mouse_pos):
			self.restart()
			self.show_main_menu = False
			self.show_menu = False
		if self.options_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_options = True
		if self.level_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_level = True
		if self.quit_button.checkForInput(mouse_pos):
			self.terminate_game()

	def process_options(self, mouse_pos):
		if self.human_choice.checkForInput(mouse_pos):
			self.ai_green = False
			self.ai_magenta = False
		if self.ai_starts.checkForInput(mouse_pos):
			self.ai_green = True
			self.ai_magenta = False
		if self.ai_strikes_back.checkForInput(mouse_pos):
			self.ai_green = False
			self.ai_magenta = True
		if self.options_back.checkForInput(mouse_pos):
			self.show_options = False
			self.show_main_menu = True

	def process_level(self, mouse_pos):
		if self.old_ai_choice.checkForInput(mouse_pos):
			self.level = Level.OLD
		if self.imp_old_ai_choice.checkForInput(mouse_pos):
			self.level = Level.OLD_IMP
		if self.new_ai_choice.checkForInput(mouse_pos):
			self.level = Level.NEW
		if self.level_back.checkForInput(mouse_pos):
			self.show_level = False
			self.show_main_menu = True

	def process_menu(self, mouse_pos):
		if self.show_main_menu:
			self.process_main_menu(mouse_pos)
		elif self.show_options:
			self.process_options(mouse_pos)
		elif self.show_level:
			self.process_level(mouse_pos)

	def process_human_turn(self, mouse_pos):
		cell = self.graphics.board_coords(mouse_pos)  # what square is the mouse in?
		if self.board.on_board(cell):
			if not self.hop:
				piece = self.board.location(cell).occupant
				if piece is not None and piece.color == self.turn:
					self.selected_piece = cell
				elif self.selected_piece is not None and cell in self.board.legal_moves(self.selected_piece):
					self.board.move_piece(self.selected_piece, cell)

					if cell not in self.board.adjacent(self.selected_piece):
						self.hop = True
						self.selected_piece = cell
					else:
						self.end_turn()

			elif self.hop:
				if self.selected_piece is not None and cell in self.board.legal_moves(self.selected_piece, self.hop):
					self.board.move_piece(self.selected_piece, cell)
					self.selected_piece = cell
				else:
					self.end_turn()

	def event_loop(self):
		"""
		The event loop. This is where events are triggered
		(like a mouse click) and then effect the game state.
		"""
		if self.selected_piece is not None:
			self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

		for event in pygame.event.get():
			if event.type == QUIT:
				self.terminate_game()

			if not self.show_menu and event.type == self.TICK:
				self.graphics.tick()

			if not self.show_menu and event.type == self.AI_TICK:
				if not self.is_human_turn() and not self.end:
					self.perform_ai_turn()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.show_menu = not self.show_menu
					self.show_main_menu = not self.show_options and self.show_menu
					if not self.is_human_turn():
						self.perform_ai_turn()

			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				if self.show_menu:
					self.process_menu(mouse_pos)
				elif not self.end and self.is_human_turn():
					cell = self.graphics.board_coords(mouse_pos)  # what square is the mouse in?
					if self.board.on_board(cell):
						if not self.hop:
							if self.board.location(cell).occupant != None and self.board.location(cell).occupant.color == self.turn:
								self.selected_piece = cell

							elif self.selected_piece != None and cell in self.board.legal_moves(self.selected_piece):

								self.board.move_piece(self.selected_piece, cell)

								if cell not in self.board.adjacent(self.selected_piece):
									self.hop = True
									self.selected_piece = cell

								else:
									self.end_turn()

						elif self.hop == True:
							if self.selected_piece != None and cell in self.board.legal_moves(self.selected_piece, self.hop):
								self.board.move_piece(self.selected_piece, cell)
								self.selected_piece = cell
							else:
								self.end_turn()
			if self.show_menu:
				if self.show_main_menu:
					self.display_main_menu()
				elif self.show_options:
					self.display_options()
				elif self.show_level:
					self.display_level()

	def is_human_turn(self):
		return not self.ai_magenta and self.turn == MAGENTA or not self.ai_green and self.turn == GREEN

	def display_main_menu(self):
		self.graphics.screen.fill("black")

		menu_text = self.get_font(100).render("MAIN MENU", True, "#b68f40")
		menu_rect = menu_text.get_rect(center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))

		self.graphics.screen.blit(menu_text, menu_rect)

		mouse_pos = pygame.mouse.get_pos()
		for button in [self.play_button, self.restart_button, self.options_button, self.level_button, self.quit_button]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)
		pygame.display.update()

	def display_options(self):
		mouse_pos = pygame.mouse.get_pos()

		self.graphics.screen.fill("black")

		options_text = self.get_font(45).render("GAME OPTIONS", True, "#b68f40")
		options_rect = options_text.get_rect(center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))
		self.graphics.screen.blit(options_text, options_rect)

		self.human_choice.selected = not (self.ai_green or self.ai_magenta)
		self.ai_starts.selected = self.ai_green
		self.ai_strikes_back.selected = self.ai_magenta

		for button in [self.human_choice, self.ai_starts, self.ai_strikes_back, self.options_back]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)

		pygame.display.update()

	def display_level(self):
		mouse_pos = pygame.mouse.get_pos()

		self.graphics.screen.fill("black")

		options_text = self.get_font(45).render("AI LEVEL OPTIONS", True, "#b68f40")
		options_rect = options_text.get_rect(
			center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))
		self.graphics.screen.blit(options_text, options_rect)

		self.old_ai_choice.selected = self.level == Level.OLD
		self.imp_old_ai_choice.selected = self.level == Level.OLD_IMP
		self.new_ai_choice.selected = self.level == Level.NEW

		for button in [self.old_ai_choice, self.imp_old_ai_choice, self.new_ai_choice, self.level_back]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)

		pygame.display.update()



	def restart(self):
		self.end = False
		self.green = 1
		self.magenta = 1
		self.hop = False
		self.turn = GREEN
		self.selected_legal_moves = []
		self.selected_piece = None
		self.board.matrix = self.board.new_board()
		self.graphics.draw_message("Next Turn: Magenta. Counter: " + str(self.magenta))
		self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

	def update(self):
		"""Calls on the graphics class to update the game display."""
		if not self.show_menu:
			self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)


	def terminate_game(self):
		Game.run = False

	def main(self):
		""""This executes the game and controls its flow."""
		self.setup()

		self.graphics.draw_message("Next Turn: Green. Counter: " + str(self.green))

		while Game.run: # main game loop
			self.event_loop()
			self.update()

		pygame.quit()
		sys.exit()

	def end_turn(self):
		print("End of turn")
		print("==============================================================================================")
		"""
		End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes.
		"""
		if self.post_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message("MAGENTA WINS!")
			else:
				self.graphics.draw_message("GREEN WINS!")
			self.selected_piece = None
			self.selected_legal_moves = []
			self.hop = False
			return

		if self.turn == GREEN:
			self.green += 1
			self.turn = MAGENTA
			self.graphics.draw_message("Next Turn: Magenta. Counter: " + str(self.magenta))

		else:
			self.magenta += 1
			self.turn = GREEN
			self.graphics.draw_message("Next Turn: Green. Counter: " + str(self.green))

		self.selected_piece = None
		self.selected_legal_moves = []
		self.hop = False

		if self.pre_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message("MAGENTA WINS!")
			else:
				self.graphics.draw_message("GREEN WINS!")
		#print("Checking AI Turn")
		if not self.end:
			self.perform_ai_turn()

	def get_ai(self):
		match self.level:
			case Level.OLD:
				return self.oldai
			case Level.OLD_IMP:
				return self.impoldai
			case Level.NEW:
				return self.ai

	def perform_ai_turn(self):
		print("self.turn", self.turn, ' ai m ', self.ai_magenta)
		if self.turn == MAGENTA and self.ai_magenta:
			self.get_ai().turn_magenta(self.magenta)
			if self.post_check_for_endgame():
				self.end = True
				self.graphics.draw_message("GREEN WINS!")
				return

			self.magenta += 1
			self.turn = GREEN
			self.graphics.draw_message("Next Turn: Green. Counter: " + str(self.green))
			if self.pre_check_for_endgame():
				self.end = True
				self.graphics.draw_message("MAGENTA WINS!")
				return
			print("self.turn", self.turn, ' ai g ', self.ai_green)
		elif self.turn == GREEN and self.ai_green:
			self.get_ai().turn_green(self.green)

			if self.post_check_for_endgame():
				self.end = True
				self.graphics.draw_message("MAGENTA WINS!")
				return

			self.green += 1
			self.turn = MAGENTA
			self.graphics.draw_message("Next Turn: Magenta. Counter: " + str(self.magenta))
			if self.pre_check_for_endgame():
				self.end = True
				self.graphics.draw_message("GREEN WINS!")
				return

	def check_if_magenta_completes(self):
		for x in range(4, 8):
			for y in range(4, 8):
				piece = self.board.location((x, y)).occupant
				if piece is None or piece.color != MAGENTA:
					return False
		return True

	def check_if_green_completes(self):
		for x in range(4, 8):
			for y in range(4):
				piece = self.board.location((x, y)).occupant
				if piece is None or piece.color != GREEN:
					return False
		return True

	def check_if_magenta_stays(self):
		for x in range(4, 8):
			for y in range(4):
				piece = self.board.location((x, y)).occupant
				if piece is not None and piece.color == MAGENTA:
					return True
		return False

	def check_if_green_stays(self):
		for x in range(4, 8):
			for y in range(4, 8):
				piece = self.board.location((x, y)).occupant
				if piece is not None and piece.color == GREEN:
					return True
		return False

	def pre_check_for_endgame(self):
		"""
		Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
		"""
		if self.turn == GREEN:
			if self.check_if_magenta_completes():
				return True
		if self.turn == MAGENTA:
			if self.check_if_green_completes():
				return True
		for x in range(8):
			for y in range(8):
				if self.board.location((x,y)).occupant is not None and self.board.location((x,y)).occupant.color == self.turn:
					if self.board.legal_moves((x,y)) != []:
						return False

		return True

	def post_check_for_endgame(self):
		"""
		Checks to see if a player has stayed in his field for longer than 50 turns or moves back after 50th turn
		"""
		print("post check for end: g ", self.green, " s? ", self.check_if_green_stays(), " m ", self.magenta, " ms? ", self.check_if_magenta_stays() )
		if self.turn == GREEN:
			if self.green > 50 and self.check_if_green_stays():
				return True
		if self.turn == MAGENTA:
			if self.magenta > 50 and self.check_if_magenta_stays():
				return True

		return False

def main():
	game = Game()
	game.main()

if __name__ == "__main__":
	main()