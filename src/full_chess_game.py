# full_chess_game.py

from stockfish import Stockfish
import chess
from reason_features import get_reasons
from explanation import generate_explanation

# =====================================
# إعداد Stockfish
# =====================================
STOCKFISH_PATH = r"C:\chess\stockfish\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(STOCKFISH_PATH)
stockfish.set_skill_level(20)  # مستوى الذكاء (0-20)

# =====================================
# إعداد الرقعة
# =====================================
board = chess.Board()

# رموز Unicode للقطع
UNICODE_PIECES = {
    'r':'♜', 'n':'♞', 'b':'♝', 'q':'♛', 'k':'♚', 'p':'♟',
    'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♕', 'K':'♔', 'P':'♙'
}

def print_board():
    """طباعة الرقعة بشكل رسومي بالـ Console"""
    print("\nCurrent Board:")
    print("  a b c d e f g h")
    for rank in range(8, 0, -1):
        row = f"{rank} "
        for file in "abcdefgh":
            square = chess.parse_square(f"{file}{rank}")
            piece = board.piece_at(square)
            row += UNICODE_PIECES[piece.symbol()] if piece else "·"
            row += " "
        print(row + str(rank))
    print("  a b c d e f g h\n")

# =====================================
# بداية اللعبة
# =====================================
print("Welcome to Chess XAI Game!\n")
print_board()

while not board.is_game_over():
    # جلب الحركات القانونية
    legal_moves = [move.uci() for move in board.legal_moves]
    
    print("Legal moves:", legal_moves)
    
    # إدخال حركة من المستخدم
    user_move = input("Enter your move (e.g., e2e4) or 'quit': ").strip()
    if user_move.lower() == "quit":
        print("Game ended by user.")
        break
    
    if user_move not in legal_moves:
        print("Illegal move! Try again.\n")
        continue
    
    # تنفيذ الحركة
    move = chess.Move.from_uci(user_move)
    board.push(move)
    
    # تحديث Stockfish
    stockfish.set_fen_position(board.fen())
    evaluation = stockfish.get_evaluation()
    
    # تفسير الحركة XAI
    reasons = get_reasons(board.fen(), move.uci())
    explanation = generate_explanation(move.uci(), reasons)
    
    # عرض النتائج
    print("\n--- Move Explanation ---")
    print(f"Move: {move.uci()}")
    print(explanation)
    print("Evaluation:", evaluation)
    print("-------------------------\n")
    
    # طباعة الرقعة بعد الحركة
    print_board()

# =====================================
# نهاية اللعبة
# =====================================
print("Game over!")
print("Final Board:")
print_board()
print("Result:", board.result())

