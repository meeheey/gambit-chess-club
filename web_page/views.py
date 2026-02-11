# web_page/views.py
import random
import chess
from django.shortcuts import render

from .models import ClubMember, ClubTournament
from puzzles.models import Puzzle

# Piece symbols mapping
PIECE_SYMBOLS = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

def remove_consecutive_duplicates(move_str):
    """Remove consecutive identical lowercase letters"""
    if not move_str:
        return move_str
    result = move_str[0]
    for c in move_str[1:]:
        if not (c.islower() and c == result[-1]):
            result += c
    return result

def index(request):
    club_players = ClubMember.objects.filter(is_active=True).order_by('order', '-rating')

    tournaments = ClubTournament.objects.all().order_by('status', 'end_date')[:3]

    puzzle_ids = list(Puzzle.objects.values_list('id', flat=True))
    puzzle = Puzzle.objects.get(id=random.choice(puzzle_ids))

    moves_uci = puzzle.moves.split()
    first_move = moves_uci[0]

    # Puzzle FEN after first move
    board = chess.Board(puzzle.fen)
    board.push_uci(first_move)
    puzzle_fen = board.fen()

    # Generate cleaned solution
    board_solution = chess.Board(puzzle.fen)
    moves_clean = []

    for move_uci in moves_uci[1:]:  # skip first move
        move = chess.Move.from_uci(move_uci)
        san = board_solution.san(move)

        # Replace piece letters with symbols
        piece = board_solution.piece_at(move.from_square)
        if piece:
            symbol = PIECE_SYMBOLS[piece.symbol()]
            if san[0] in "KQRBN":
                san = symbol + san[1:]

        # Remove x and all non-alphanumeric except piece symbols
        san_clean = "".join(c for c in san if c != 'x' and (c.isalnum() or c in PIECE_SYMBOLS.values()))

        # Remove consecutive identical lowercase letters
        san_clean = remove_consecutive_duplicates(san_clean)

        moves_clean.append(san_clean)
        board_solution.push(move)

    # Number moves: 1. move1 move2 2. move3 move4 ...
    numbered_solution = []
    for i in range(0, len(moves_clean), 2):
        white_move = moves_clean[i]
        black_move = moves_clean[i+1] if i+1 < len(moves_clean) else ""
        numbered_solution.append(f"{i//2 + 1}. {white_move} {black_move}".strip())

    text_solution = "  ".join(numbered_solution)

    return render(request, 'web_page/home.html', {
        'club_players': club_players,
        'tournaments': tournaments,
        'puzzle': puzzle,
        'puzzle_fen': puzzle_fen,
        'puzzle_first_move': first_move,
        'puzzle_solution': text_solution,
    })

def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'web_page/home.html')