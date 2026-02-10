from stockfish import Stockfish
import chess
from reason_features import get_reasons
from explanation import generate_explanation

# =====================================
# إعداد Stockfish
# =====================================
stockfish = Stockfish(r"C:\Users\amine\Desktop\python-chess-ai-yt-master\stockfish\stockfish-windows-x86-64-avx2.exe")
stockfish.set_skill_level(20)

# =====================================
# إعداد الرقعة
# =====================================
board = chess.Board()
print("Initial Board:")
print(board, "\n")

# =====================================
# تحليل كل حركة قانونية
# =====================================
legal_moves = list(board.legal_moves)

for move in legal_moves:
    board.push(move)
    stockfish.set_fen_position(board.fen())
    evaluation = stockfish.get_evaluation()

    # مرّر FEN والحركة كـ string
    reasons = get_reasons(board.fen(), move.uci())
    explanation = generate_explanation(move.uci(), reasons)

    print(explanation)
    print("Evaluation:", evaluation)
    print("-" * 50)

    board.pop()
