# reason_features.py
import chess

def get_reasons(board_fen, move_uci):
    """
    board_fen : string (FEN) للوضع الحالي
    move_uci : string مثل "g1h3"
    """
    temp_board = chess.Board(board_fen)  # أنشئ نسخة جديدة من FEN

    move = chess.Move.from_uci(move_uci)

    # إذا لم تكن الحركة قانونية على الرقعة → تجاهلها
    if move not in temp_board.legal_moves:
        return {"Immediate Threat": False,
                "Tactical Gain": False,
                "Open Lines": False,
                "Control Center": False,
                "Restrict Opponent": False,
                "Long-term Pressure": False}

    temp_board.push(move)

    reasons = {
        "Immediate Threat": False,
        "Tactical Gain": False,
        "Open Lines": False,
        "Control Center": False,
        "Restrict Opponent": False,
        "Long-term Pressure": False
    }

    # مثال: إذا الحركة تهدد قطعة الخصم مباشرة
    attackers = temp_board.attackers(not temp_board.turn, move.to_square)
    if attackers:
        reasons["Immediate Threat"] = True

    return reasons
