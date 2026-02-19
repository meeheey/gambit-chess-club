import random
import chess
from django.shortcuts import render

from .models import Article, ArticleImage, ClubMember, ClubTournament, LeagueStatisticsField
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

def get_valid_puzzle(max_attempts=10):
    """Try to get a valid puzzle, deleting invalid ones"""
    attempts = 0
    while attempts < max_attempts:
        puzzle_ids = list(Puzzle.objects.values_list('id', flat=True))
        if not puzzle_ids:
            return None
        
        puzzle_id = random.choice(puzzle_ids)
        try:
            puzzle = Puzzle.objects.get(id=puzzle_id)
            
            # Validate the puzzle
            moves_uci = puzzle.moves.split()
            if len(moves_uci) < 2:
                # Invalid puzzle with insufficient moves
                puzzle.delete()
                attempts += 1
                continue
                
            first_move = moves_uci[0]
            
            # Test if we can process the puzzle without errors
            board = chess.Board(puzzle.fen)
            board.push_uci(first_move)
            
            board_solution = chess.Board(puzzle.fen)
            moves_clean = []
            
            for move_uci in moves_uci[1:]:
                try:
                    move = chess.Move.from_uci(move_uci)
                    # This will raise AssertionError if move is illegal
                    san = board_solution.san(move)
                    board_solution.push(move)
                except (AssertionError, ValueError) as e:
                    # Invalid move found - delete the puzzle
                    puzzle.delete()
                    raise ValueError(f"Invalid move in puzzle {puzzle.id}: {e}")
            
            # If we get here, puzzle is valid
            return puzzle
            
        except (Puzzle.DoesNotExist, ValueError) as e:
            # Puzzle was deleted or invalid, try another one
            attempts += 1
            continue
    
    return None

def index(request):
    club_players = ClubMember.objects.filter(is_active=True).order_by('order', '-rating')

    articles = Article.objects.filter(is_published=True).order_by('-published_at')[:8]

    tournaments = ClubTournament.objects.all().order_by('status', 'end_date')[:3]

    statistics_fields = LeagueStatisticsField.objects.filter(is_active=True).order_by('order')

    # Get a valid puzzle
    puzzle = get_valid_puzzle()
    
    # If no valid puzzles found, render without puzzle
    if not puzzle:
        return render(request, 'web_page/home.html', {
            'club_players': club_players,
            'articles': articles,
            'tournaments': tournaments,
            'puzzle': None,
        })
    
    try:
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
                if san and san[0] in "KQRBN":
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
            'articles': articles,
            'tournaments': tournaments,
            'statictics_fields': statistics_fields,
            'puzzle': puzzle,
            'puzzle_fen': puzzle_fen,
            'puzzle_first_move': first_move,
            'puzzle_solution': text_solution,
        })
        
    except (AssertionError, ValueError) as e:
        # If we encounter an error during processing, delete the puzzle and try again
        puzzle.delete()
        # Recursively call index to try another puzzle
        return index(request)
    
def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, "web_page/list.html", {
        "articles": articles
    })


def article_detail(request, pk):
    article = Article.objects.get(pk=pk, is_published=True)
    return render(request, "web_page/detail.html", {
        "article": article
    })

def gallery_view(request):
    images = ArticleImage.objects.select_related("article").all()

    return render(request, "web_page/gallery.html", {
        "images": images
    })