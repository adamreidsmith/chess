# Chess by Adam R. Smith

WHITE = 'white'
BLACK = 'black'

import random

class Chess:

	def __init__(self):
		self.turn = WHITE
		self.board = {}
		self.initialize_board()
		self.all_moves = []
		self.promotion_required = False
		self.promotion_pos = (-1,-1)

	def initialize_board(self):
		for i in range(8):
			self.board[(1,i)] = Pawn(BLACK)
			self.board[(6,i)] = Pawn(WHITE)

		piece_order = [Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
        
		for i in range(8):
			self.board[(0,i)] = piece_order[i](BLACK)
			self.board[(7,i)] = piece_order[i](WHITE)

		# Append each piece's starting position to its pos_list
		for key in self.board:
			self.board[key].pos_list.append(key)

	def print_board(self, board=None):
		board_view = [[' ' for _ in range(8)] for _ in range(8)]

		if board is None:
			board = self.board

		for pos in board:
			board_view[pos[0]][pos[1]] = board[pos].uni_char

		print('\n    A    B    C    D    E    F    G    H')
		for i, row in enumerate(board_view):
			print(str(8-i) + ' ' + str(row) + ' ' + str(8-i))
		print('    A    B    C    D    E    F    G    H\n')

	def move_piece_basic(self, target, destination):
		# Move a piece at position 'target' to position 'destination'

		# Don't move if destination position is already occupied
		if destination in self.board:
			print('Destination ' + str(destination) + ' already occupied.')
			return

		if target not in self.board:
			print('No piece located at ' + str(target) + '.')
			return

		self.board[target].pos_list.append(destination)  # Append the destination to the pos_list
		self.board[destination] = self.board[target]  # Move the piece to a new position
		del self.board[target]
		self.all_moves.append(destination)

	def do_move(self, move):
		# Complete a full move
		# Returns (start_pos, end_pos, captured_piece(rook_init_pos if castle is True), 
		# captured_piece_pos (rook_final_pos if castle is True), castle)

		captured = None

		if not move[1][1]:
			# Normal move
			if move[1][0] in self.board:
				captured = self.board[move[1][0]]
				del self.board[move[1][0]]
			self.move_piece_basic(move[0], move[1][0])
			return (move[0], move[1][0], captured, move[1][0], False)

		else:
			# Special move
			if self.board[move[0]].name == 'pawn':
				# En Passant
				captured = self.board[move[1][1]]
				del self.board[move[1][1]]
				self.move_piece_basic(move[0], move[1][0])
				return (move[0], move[1][0], captured, move[1][1], False)

			if self.board[move[0]].name == 'king':
				# Castling
				rook_init_pos = (move[0][0],7) if move[1][0][1] == 6 else (move[0][0],0)
				self.move_piece_basic(move[0], move[1][0])
				self.move_piece_basic(rook_init_pos, move[1][1])
				return (move[0], move[1][0], rook_init_pos, move[1][1], True)

	def undo_move(self, target, destination):
		# Move a piece from 'target' to 'destination'
		# Only use to undo moves

		self.board[destination] = self.board[target]
		del self.board[target]
		del self.board[destination].pos_list[-1]
		del self.all_moves[-1]

	def can_see_king(self, color):
		# Tests if any piece of the given color can see the opposite color king
		piece_list = [self.board[pos] for pos in self.board if self.board[pos].color == color]
		
		opposite_king_pos = next(pos for pos in self.board if self.board[pos].name == 'king' and self.board[pos].color != color)

		for piece in piece_list:
			if opposite_king_pos in [move[0] for move in piece.available_moves(self.board, self.all_moves)]:
				return True
		return False

	def is_in_check(self, color):
		# Checks if player specified by 'color' is in check
		if color == WHITE:
			return self.can_see_king(BLACK)
		return self.can_see_king(WHITE)

	def play_in_terminal(self):
		# Main method to play the game

		print('\nWelcome to chess.\n\
Move a piece by entering its starting position immediately\n\
followed by its final position (e.g. \'a2a4\' or \'G8F6\'). Enter\n\
\'q\' or \'quit\' to quit. Enter \'h\' or \'help\' for help.')

		while True:
			quit = False
			self.print_board()

			if not self.has_move(self.turn):
				if self.is_in_check(self.turn):
					winner = 'White' if self.turn == BLACK else 'Black'
					print('%s wins!' % winner)
					break
				print('Stalemate!')
				break

			# Get a move and ensure it is valid
			while True:
				move = self.get_move()
				if move is None:
					quit = True
					break
				if move == 'help':
					moves = self.get_available_moves(self.turn)
					print('\n%s\'s available moves:' % self.turn.capitalize())
					print(moves)
					print()
					continue
				if move[0] not in self.board:
					print('There is no piece in that space.')
					continue
				if self.board[move[0]].color != self.turn:
					print('You must move a ' + self.turn + ' piece.')
					continue
				selected_piece_available_moves = self.board[move[0]].available_moves(self.board, self.all_moves)
				valid_dests = [m[0] for m in selected_piece_available_moves]
				if not move[1] in valid_dests:
					print('Invalid move. Try again.')
					continue
				dest_plus_info = next(m for m in selected_piece_available_moves if m[0] == move[1])
				move = (move[0], dest_plus_info)
				if not self.is_valid_move(move):
					print('Invalid move. Try again.')
					continue
				break
			
			if quit: break
			
			# Move pieces and remove captured pieces from the board
			self.do_move(move)

			# Promotion
			promo_row = 0 if self.turn == WHITE else 7
			pos = self.all_moves[-1]
			if pos[0] == promo_row and self.board[pos].name == 'pawn':
				piece_class = self.get_promo_input()
				old_pawn = self.board[pos]
				del self.board[pos]
				self.board[pos] = piece_class(old_pawn.color)
				self.board[pos].pos_list = old_pawn.pos_list

			self.turn = WHITE if self.turn == BLACK else BLACK

	def get_move(self):
		try:
			move = input(self.turn.capitalize() + '\'s turn. Enter move: ')
			move = move.lower()
			if move == 'q' or move == 'quit':
				return None
			if move == 'h' or move == 'help':
				return 'help'
			return ((8-int(move[1]), ord(move[0])-97), (8-int(move[3]), ord(move[2])-97))
		except:
			print('Error decoding input. Please try again.')
			return self.get_move()

	def has_move(self, color):
		# Checks if player specified by 'color' has a valid move

		# Get all possible moves specified by each pieces available_moves method
		moves = []
		for pos in self.board:
			if self.board[pos].color == color:
				piece_moves = self.board[pos].available_moves(self.board, self.all_moves)
				for move in piece_moves:
					moves.append((pos, move))

		for move in moves:
			if self.is_valid_move(move):
				return True
		return False

	def is_valid_move(self, move):
		# Tests if a move will put the player in check or not
		# move is of the form (start_pos, (destination, special_info))
		pos = move[0]
		destination = move[1][0]
		if not move[1][1] or self.board[pos].name != 'king':  # If move is not a castling move

			# Get the correct piece and place to ressurect (captured piece)
			if move[1][1] and self.board[pos].name == 'pawn':
				piece_to_ressurect = self.board[move[1][1]]
				place_to_ressurect = move[1][1]
			else:
				piece_to_ressurect = None if destination not in self.board else self.board[destination]
				place_to_ressurect = destination

			# Remove captured piece if applicable
			if piece_to_ressurect:
				del self.board[place_to_ressurect]

			self.move_piece_basic(pos, destination)  # Move piece
			in_check = self.is_in_check(self.board[destination].color)  # Check if checkmate is present
			self.undo_move(destination, pos)  # Undo move

			# Ressurect the captured piece
			if piece_to_ressurect:
				self.board[place_to_ressurect] = piece_to_ressurect

			return not in_check

		# If move is castling
		rook_init_pos = (pos[0],7) if move[1][0][1] == 6 else (pos[0],0)
		self.move_piece_basic(pos, destination)  # Move king
		self.move_piece_basic(rook_init_pos, move[1][1])  # Move rook
		in_check = self.is_in_check(self.board[destination].color)  # Check if checkmate is present
		self.undo_move(move[1][1], rook_init_pos)  # Unmove rook
		self.undo_move(destination, pos)  # Unmove king

		if in_check:
			return False

		# Check if king moves through a position where it would be in check
		castling_dir = 1 if move[1][0][1] == 6 else -1
		self.move_piece_basic(pos, (pos[0], pos[1]+castling_dir))
		in_check = self.is_in_check(self.board[(pos[0], pos[1]+castling_dir)].color)  # Check if checkmate is present
		self.undo_move((pos[0], pos[1]+castling_dir), pos)

		return not in_check

	def get_promo_input(self):
		try:
			piece = input('What would you like to promote your pawn to? ').lower()
			return {'q':Queen, 'queen':Queen, 'k':Knight, 'knight':Knight, 'r':Rook, \
			'rook':Rook, 'b':Bishop, 'bishop':Bishop}[piece]
		except:
			print('Invalid response. Enter \'queen\', \'knight\', \'rook\', or \'bishop\'.')
			return self.get_promo_input()

	def get_available_moves(self, color):
		moves = []
		for pos in self.board:
			if self.board[pos].color == color:
				piece_moves = self.board[pos].available_moves(self.board, self.all_moves)
				for m in piece_moves:
					moves.append((pos, m))

		# Delete invalid moves
		for i, move in reversed(list(enumerate(moves))):
			if not self.is_valid_move(move):
				del moves[i]

		if not moves:
			print('No available moves.')
			return

		moves = [(move[0], move[1][0]) for move in moves]

		for i, move in enumerate(moves):
			moves[i] = (chr(move[0][1]+97).upper() + str(8-move[0][0]) + ' to ' + \
				chr(move[1][1]+97).upper() + str(8-move[1][0]))

		return moves

	########################################################################################

	def play_turn(self, move=None, promotion=None):
		'''
		Used for playing a turn and returning data
		move is of the form (start_pos, end_pos)
		
		ERROR CODES:
			(1, winner)				A player won the game
			(2, 'stalemate')		Stalemate
			(3, 'quit')				Signal to quit the game
			(4, 'promotion')		Need to promote a pawn before the next move
			(5, 'promo failed')		Promotion failed
			(6, 'promo sucessful')	Promotion successful
			(7, available moves)	Return a list of available moves for the current turn
			(-2, 'no piece')		No piece in that space
			(-3, 'wrong color')		Wrong color selected
			(-1, 'invalid')			Invalid move
			(-4, 'move error')		Error decoding move
			(0, color)				Successful turn by 'color'
		'''

		if type(move) == str:
			try:
				move = move.lower()
				if move == 'q' or move == 'quit':
					return (self.board, 3, 'quit')
				if move == 'h' or move == 'help':
					return (self.board, 7, self.get_available_moves(self.turn))
				move = ((8-int(move[1]), ord(move[0])-97), (8-int(move[3]), ord(move[2])-97))
			except:
				return (self.board, -4, 'move error')

		if self.promotion_required:
			if not promotion:
				return (self.board, 5, 'promo failed')
			try:
				promo_piece = {'q':Queen, 'queen':Queen, 'k':Knight, 'knight':Knight, \
				'r':Rook, 'rook':Rook, 'b':Bishop, 'bishop':Bishop}[promotion.lower()]
			except:
				return (self.board, 5, 'promo failed')
			old_pawn = self.board[self.promotion_pos]
			del self.board[self.promotion_pos]
			self.board[self.promotion_pos] = promo_piece(old_pawn.color)
			self.board[self.promotion_pos].pos_list = old_pawn.pos_list
			self.promotion_required = False
			self.turn = WHITE if self.turn == BLACK else BLACK
			return (self.board, 6, 'promo sucessful')

		if move is None:
			return (self.board, 3, 'quit')

		if move[0] not in self.board:
			return (self.board, -2, 'no piece')

		if self.board[move[0]].color != self.turn:
			return (self.board, -3, 'wrong color')

		selected_piece_available_moves = self.board[move[0]].available_moves(self.board, self.all_moves)
		valid_dests = [m[0] for m in selected_piece_available_moves]
		if not move[1] in valid_dests:
			return (self.board, -1, 'invalid')
		dest_plus_info = next(m for m in selected_piece_available_moves if m[0] == move[1])
		move = (move[0], dest_plus_info)
		if not self.is_valid_move(move):
			return (self.board, -1, 'invalid')
		
		# Move pieces and remove captured pieces from the board
		self.do_move(move)

		# Promotion
		promo_row = 0 if self.turn == WHITE else 7
		pos = self.all_moves[-1]
		if pos[0] == promo_row and self.board[pos].name == 'pawn':
			self.promotion_required = True
			self.promotion_pos = pos
			return (self.board, 4, 'promotion')

		self.turn = WHITE if self.turn == BLACK else BLACK

		if not self.has_move(self.turn):
			if self.is_in_check(self.turn):
				winner = WHITE if self.turn == BLACK else BLACK
				return (self.board, 1, winner)
			return (self.board, 2, 'stalemate')

		return (self.board, 0, WHITE if self.turn == BLACK else BLACK)

	def get_board(self):
		return self.board

	def get_turn(self):
		return self.turn

	def get_promotion(self):
		return self.promotion_required

	def get_random_move(self, color):
		moves = []
		for pos in self.board:
			if self.board[pos].color == color:
				piece_moves = self.board[pos].available_moves(self.board, self.all_moves)
				for m in piece_moves:
					moves.append((pos, m))

		if not moves:
			return None

		random.shuffle(moves)
		move = moves.pop()
		while not self.is_valid_move(move):
			if len(moves) == 0:
				return None
			random.shuffle(moves)
			move = moves.pop()

		return (move[0], move[1][0])

	def get_smart_move(self, color):
		if self.promotion_required:
			return None

		# Get all potential moves
		moves = []
		for pos in self.board:
			if self.board[pos].color == color:
				piece_moves = self.board[pos].available_moves(self.board, self.all_moves)
				for move in piece_moves:
					moves.append((pos, move))

		# Delete invalid moves
		for i, move in reversed(list(enumerate(moves))):
			if not self.is_valid_move(move):
				del moves[i]

		# Get moves in which a piece is captured
		capture_moves = []
		for move in moves:
			if move[1][0] in self.board:
				capture_moves.append(move)

		# Get moves in which the opposing king is put in check
		check_moves = []
		for move in moves:
			pos_start, pos_final, captured, captured_pos, castle = self.do_move(move)
			if self.can_see_king(color):
				check_moves.append(move)
			if castle:
				self.undo_move(captured_pos, captured)
				self.undo_move(pos_final, pos_start)
			else:
				self.undo_move(pos_final, pos_start)
				if captured:
					self.board[captured_pos] = captured

		# Get moves which capture and put the opposing king in check
		capture_and_check_moves = []
		for move in capture_moves:
			if move in check_moves:
				capture_and_check_moves.append(move)

		# Return a random move fromt he best available list
		if capture_and_check_moves:
			random.shuffle(capture_and_check_moves)
			move = capture_and_check_moves.pop()
			return (move[0], move[1][0])

		if check_moves:
			random.shuffle(check_moves)
			move = check_moves.pop()
			return (move[0], move[1][0])

		if capture_moves:
			random.shuffle(capture_moves)
			move = capture_moves.pop()
			return (move[0], move[1][0])

		if not moves:
			return None

		random.shuffle(moves)
		move = moves.pop()
		return (move[0], move[1][0])

	########################################################################################

class Piece:

	def __init__(self, color):
		self.color = color
		self.pos_list = []

	def no_conflict(self, board, pos):
		# Checks if moving to position 'pos' is viable
		if is_on_board(pos) and (pos not in board or board[pos].color != self.color):
			return True
		return False

	def collect_linear_moves(self, board, directions):
		# Gets all free spaces in the directions specified from a piece
		moves = []
		pos = self.pos_list[-1]
		for direc in directions:
			pos_to_check = pos
			while True:
				pos_to_check = (pos_to_check[0]+direc[0], pos_to_check[1]+direc[1])
				if self.no_conflict(board, pos_to_check):
					moves.append((pos_to_check, None))
				else:
					break
				if pos_to_check in board:
					break
		return moves

	def test_move_list(self, board, move_list):
		# Tests a list of relative moves to remove conflicts
		pos = self.pos_list[-1]
		moves = [((move[0]+pos[0], move[1]+pos[1]), None) for move in move_list]
		for i, move in reversed(list(enumerate(moves))):
			if not self.no_conflict(board, move[0]):
				del moves[i]
		return moves


cardinals = [(1,0), (0,1), (-1,0), (0,-1)]
diagonals = [(1,1), (-1,-1), (-1,1), (1,-1)]


class Pawn(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'pawn'
		self.uni_char = '♙' if color == BLACK else '♟'
		self.dir = 1 if color == BLACK else -1

	def available_moves(self, board, all_moves):
		# Returns a list of tuples of length 2
		# The first item is the available move final position
		# The second item is None for a normal move and the position of the attacked piece for En Passant moves
		moves = []
		pos = self.pos_list[-1]
		for dest in [(pos[0]+self.dir, pos[1]-1), (pos[0]+self.dir, pos[1]+1)]:
			if dest in board and self.no_conflict(board, dest):
				moves.append((dest, None))
		if (pos[0]+self.dir, pos[1]) not in board and is_on_board((pos[0]+self.dir, pos[1])):
			moves.append(((pos[0]+self.dir, pos[1]), None))

			if len(self.pos_list) == 1 and (pos[0]+2*self.dir, pos[1]) not in board:
				moves.append(((pos[0]+2*self.dir, pos[1]), None))

		# En Passant
		en_passant_row = 4 if self.color == BLACK else 3
		# Make sure the attacking piece is in the right row for en passant
		if pos[0] == en_passant_row:
			en_passant_positions = [(pos[0], pos[1]-1), (pos[0], pos[1]+1)]
			for target_piece_pos in en_passant_positions:
				if target_piece_pos in board and board[target_piece_pos].color != self.color:
					if board[target_piece_pos].name == 'pawn':
						# Make sure the attacked pawn just moved to the position
						if len(board[target_piece_pos].pos_list) == 2 and all_moves[-1] == target_piece_pos:
							moves.append(((target_piece_pos[0]+self.dir, target_piece_pos[1]), target_piece_pos))

		return moves


class Rook(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'rook'
		self.uni_char = '♖' if color == BLACK else '♜'

	def available_moves(self, board, all_moves=None):
		return self.collect_linear_moves(board, cardinals)


class Knight(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'knight'
		self.uni_char = '♘' if color == BLACK else '♞'

	def available_moves(self, board, all_moves=None):
		knight_list = ((-1,-2), (-2,-1), (-2,1), (-1,2), (1,-2), (2,-1), (2,1), (1,2))
		return self.test_move_list(board, knight_list)


class Bishop(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'bishop'
		self.uni_char = '♗' if color == BLACK else '♝'

	def available_moves(self, board, all_moves=None):
		return self.collect_linear_moves(board, diagonals)


class Queen(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'queen'
		self.uni_char = '♕' if color == BLACK else '♛'

	def available_moves(self, board, all_moves=None):
		return self.collect_linear_moves(board, cardinals + diagonals)


class King(Piece):

	def __init__(self, color):
		super().__init__(color)
		self.name = 'king'
		self.uni_char = '♔' if color == BLACK else '♚'

	def available_moves(self, board, all_moves=None):
		# Returns a list of tuples of length 2
		# The first item is the available move final position
		# The second item is None for a normal move and the position the rook moves to for Castling moves
		king_list = ((-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1))
		moves = self.test_move_list(board, king_list)

		# Castling
		if len(self.pos_list) == 1:
			castling_row = 0 if self.color == BLACK else 7
			if (castling_row,5) not in board and (castling_row,6) not in board:
				if (castling_row,7) in board and len(board[(castling_row,7)].pos_list) == 1:
					moves.append(((castling_row,6), (castling_row,5)))

			if (castling_row,3) not in board and (castling_row,2) not in board and (castling_row,1) not in board:
				if (castling_row,0) in board and len(board[(castling_row,0)].pos_list) == 1:
					moves.append(((castling_row,2), (castling_row,3)))

		return moves

def is_on_board(pos):
	# Checks if a position is on the board
	if pos[0] >= 0 and pos[0] <= 7 and pos[1] >= 0 and pos[1] <= 7:
		return True
	return False


if __name__ == '__main__':
	chess = Chess()
	chess.play_in_terminal()

