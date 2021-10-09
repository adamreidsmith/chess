# Chess gui by Adam R. Smith

import chess

import pygame
import time
import random

from pygame.locals import *

# def random_game(smart=True, visual=False, time_step=0.2, promotion_piece='queen'):
# 	'''
# 	Play a random game.
# 	Parameters:
# 		smart[boolean]
# 			If true, smart moves will be selected. If false, random moves will be used.
# 		visual[boolean]
# 			If true, the game will be displayed in the terminal.  If false, the game
# 				will be played in the background.
# 		time_step[float]	
# 			Time step between moves for visual games.
# 		promotion_piece['queen', 'knight', 'rook', 'bishop', 'random']
# 			Choose what piece pawns are promoted to
# 	'''

# 	engine = chess.Chess()

# 	move = engine.get_smart_move(engine.get_turn()) if smart else engine.get_random_move(engine.get_turn())

# 	n_it, fail_count = 0, 0
# 	while True:
# 		if visual:
# 			engine.print_board()

# 		if promotion_piece.lower() == 'random':
# 			promo_piece = random.choice(('queen', 'knight', 'rook', 'bishop'))
# 		else:
# 			promo_piece = promotion_piece

# 		n_it += 1
# 		board, error, msg = engine.play_turn(move, promo_piece)

# 		if len(board) <= 2 or error == 2:
# 			return 'stalemate', n_it

# 		if error == 1:
# 			return msg.lower(), n_it

# 		if error not in (0, 4, 6):
# 			return 'error', n_it

# 		if n_it % 2000 == 0:
# 			move = engine.get_random_move(engine.get_turn())
# 			fail_count += 1
# 			continue

# 		if fail_count >= 3:
# 			return 'stalemate', n_it

# 		move = engine.get_smart_move(engine.get_turn()) if smart else engine.get_random_move(engine.get_turn())

# 		if visual:
# 			time.sleep(time_step)



def main():
	# The main program

	surface = create_window()
	game = Game(surface)
	game.play()
	pygame.quit()

def create_window():
	# Open a window on the display and return its surface

	title = 'Chess'
	size = (8*80, 8*80)
	pygame.init()
	surface = pygame.display.set_mode(size, 0, 0)
	pygame.display.set_caption(title)
	return surface


class Tile:
	# An object in this class represents a Rectangular tile

	def __init__(self, surface, pos, corner, width, height):
		self.surface = surface
		self.pos = pos
		self.corner = corner
		self.width = width
		self.height = height
		self.rect = pygame.Rect(corner, (width,height))
		LIGHT = pygame.Color(162, 82, 80)
		DARK = pygame.Color(242, 232, 231)
		self.color = LIGHT if sum(pos) % 2 == 0 else DARK
		self.img_names = {('pawn', 'white'):'chess_pieces/pawn_white.png',
			('pawn', 'black'):'chess_pieces/pawn_black.png',
			('rook', 'white'):'chess_pieces/rook_white.png',
			('rook', 'black'):'chess_pieces/rook_black.png',
			('knight', 'white'):'chess_pieces/knight_white.png',
			('knight', 'black'):'chess_pieces/knight_black.png',
			('bishop', 'white'):'chess_pieces/bishop_white.png',
			('bishop', 'black'):'chess_pieces/bishop_black.png',
			('queen', 'white'):'chess_pieces/queen_white.png',
			('queen', 'black'):'chess_pieces/queen_black.png',
			('king', 'white'):'chess_pieces/king_white.png',
			('king', 'black'):'chess_pieces/king_black.png'}
		self.highlighted = False
		self.highlight_alpha = 100
		self.highlight_color = (255, 0, 0)

	def draw(self, pos=None, piece=None, color=None):
		# Draw a tile and its contents

		pygame.draw.rect(self.surface, self.color, self.rect)
		if pos:
			# Load the piece image and scale it proportionally
			scale_factor = 0.75
			piece_img = pygame.image.load(self.img_names[(piece, color)])
			new_width = int(piece_img.get_width()*self.height/piece_img.get_height())
			piece_img = pygame.transform.smoothscale(piece_img,
				(int(scale_factor*new_width), int(scale_factor*self.height)))

			# Draw the image in the center of the tile
			center = (self.corner[0]+self.width//2, self.corner[1]+self.height//2)
			img_corner = (center[0]-piece_img.get_width()//2, 
				center[1]-piece_img.get_height()//2)
			self.surface.blit(piece_img, img_corner)

		if self.highlighted:
			highlight_surface = pygame.Surface((self.width, self.height))
			highlight_surface.set_alpha(self.highlight_alpha)
			highlight_surface.fill(self.highlight_color)
			self.surface.blit(highlight_surface, self.corner)

	def clicked(self, pos):
		# Determine if the position pos is within the current tile
		return self.rect.collidepoint(pos)


class Game:
	# An object of this class represents a complete game

	def __init__(self, surface):
		self.surface = surface
		self.close_clicked = False
		self.continue_game = True
		self.highlighted = None
		self.board_size = 8
		self.pause_time = 0.001
		self.bg_color = pygame.Color('grey')
		self.engine = chess.Chess()
		self.font_size = 50
		self.font = 'freesansbold.ttf'
		self.font_color = pygame.Color(0, 0, 255)
		pygame.event.set_blocked(MOUSEMOTION)
		self.end_msg = None
		self.promotion_required = False
		self.create_board()

		font = pygame.font.Font(self.font, self.font_size)
		queen_surface = font.render('QUEEN', True, self.font_color)
		knight_surface = font.render('KNIGHT', True, self.font_color)
		bishop_surface = font.render('BISHOP', True, self.font_color)
		rook_surface = font.render('ROOK', True, self.font_color)
		self.promo_surfaces = [queen_surface, knight_surface, bishop_surface, rook_surface]

		width, height = self.surface.get_width(), self.surface.get_height()
		self.promo_locs, self.promo_rects = [], []
		for i, surf in enumerate(self.promo_surfaces):
			loc = ((2*(i%2)+1)*width//4-surf.get_width()//2, (i//2+1)*height//3-surf.get_height()//2)
			self.promo_locs.append(loc)
			self.promo_rects.append(pygame.Rect(loc, (surf.get_width(), surf.get_height())))

	def create_board(self):
		self.board = []
		width = self.surface.get_width() // self.board_size
		height = self.surface.get_height() // self.board_size
		for i in range(self.board_size):
			row = []
			for j in range(self.board_size):
				corner = (j*width, i*height)
				tile = Tile(self.surface, (i,j), corner, width, height)
				row.append(tile)
			self.board.append(row)

	def play(self):
		# Play the game

		self.draw()
		while not self.close_clicked:
			result = self.handle_event()
			if result is not None:
				self.handle_result(result[0], result[1])
			self.draw_board()
			if not self.continue_game:
				msg = self.end_msg.upper() if self.end_msg == 'stalemate' else self.end_msg.upper() + ' WINS!'
				self.display_msg(msg, pause_time=0)
			if self.promotion_required:
				self.display_promo()

			pygame.display.update()
			time.sleep(self.pause_time)

	def draw(self):
		# Draw the game objects

		self.draw_board()
		pygame.display.update()

	def draw_board(self):
		# Draw the board

		chess_board = self.engine.get_board()

		for i, row in enumerate(self.board):
			for j, tile in enumerate(row):
				if (i,j) in chess_board:
					tile.draw((i,j), chess_board[(i,j)].name, chess_board[(i,j)].color)
				else:
					tile.draw()

	def handle_event(self):
		# Handle each user event by changing the game state appropriately.

		for event in pygame.event.get():
			if event.type == QUIT:
				self.close_clicked = True
				return None
			elif event.type == MOUSEBUTTONUP and self.continue_game:
				if not self.promotion_required:
					return self.handle_mouse_up(event)
				self.handle_mouse_up_promo(event)

	def handle_mouse_up(self, event):
		# Handle a click on the board
		
		pos = event.pos
		for row in self.board:
			for tile in row:
				if tile.clicked(pos):
					if self.highlighted:
						if tile.highlighted:
							tile.highlighted = False
							self.highlighted = None
							return None
						self.board[self.highlighted[0]][self.highlighted[1]].highlighted = False
						move = (self.highlighted, tile.pos)
						self.highlighted = None
						_, result, msg = self.engine.play_turn(move)
						return (result, msg)
					if tile.pos in self.engine.get_board():
						if self.engine.get_board()[tile.pos].color == self.engine.get_turn():
							self.highlighted = tile.pos
							tile.highlighted = True
					return None

	def handle_mouse_up_promo(self, event):
		# Handle clicking on the promo buttons

		promo_piece = None
		for i, rect in enumerate(self.promo_rects):
			if rect.collidepoint(event.pos):
				promo_piece = ['queen', 'knight', 'bishop', 'rook'][i]
		if promo_piece:
			self.engine.play_turn(move=None, promotion=promo_piece)
			self.promotion_required = False

	def handle_result(self, result, msg):
		# Handle the result of a move

		if result == -3:
			self.display_msg('WRONG COLOUR')
		elif result in (-1, -2):
			self.display_msg('INVALID MOVE')
		elif result == -4:
			raise RuntimeError('Error decoding move input')
		elif result == 4:
			self.promotion_required = True
		elif result in (1, 2):
			self.continue_game = False
			self.end_msg = msg

	def display_msg(self, msg, pause_time=0.75):
		# Briefly display a message on the screen

		font = pygame.font.Font(self.font, self.font_size)
		str_surface = font.render(msg, True, self.font_color)

		width = str_surface.get_width()
		height = str_surface.get_height()
		str_corner = (self.surface.get_width()//2 - width//2, self.surface.get_height()//2 - height//2)
		self.surface.blit(str_surface, str_corner)
		if pause_time:
			pygame.display.update()
			time.sleep(pause_time)

	def display_promo(self):
		# Display the options for pawn promotion

		for i, surf in enumerate(self.promo_surfaces):
			self.surface.blit(surf, self.promo_locs[i])


if __name__ == '__main__':
	main()

