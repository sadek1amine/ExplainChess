# chess_engine.py
from stockfish import Stockfish
import chess

# =====================================
# إعداد Stockfish
# =====================================
STOCKFISH_PATH = r"C:\chess\stockfish\stockfish-windows-x86-64-avx2.exe"  # ضع مسار المحرك
stockfish = Stockfish(STOCKFISH_PATH)
stockfish.set_skill_level(20)  # مستوى الذكاء (0-20)

# =====================================
# إعداد الرقعة
# =====================================
board = chess.Board()
print("Initial Board:")
print(board, "\n")

# =====================================
# جلب الحركات القانونية وتقييمها
# =====================================
legal_moves = list(board.legal_moves)

print("Evaluating all legal moves...\n")

for move in legal_moves:
    # تنفيذ الحركة على الرقعة مؤقتًا
    board.push(move)
    
    # تحديث FEN في Stockfish
    stockfish.set_fen_position(board.fen())
    
    # الحصول على التقييم
    evaluation = stockfish.get_evaluation()  # {'type': 'cp', 'value': 34} أو {'type': 'mate', 'value': 2}
    
    # طباعة الحركة والتقييم
    print(f"Move: {move.uci()}")
    print(f"Evaluation: {evaluation}")
    print("-" * 50)
    
    # التراجع عن الحركة لإرجاع الرقعة للوضع السابق
    board.pop()

