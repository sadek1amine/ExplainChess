def generate_explanation(move, reasons):
    explanation = f"Move: {move}\nReasons:\n"
    for reason, status in reasons.items():
        explanation += f"- {reason}: {'Yes' if status else 'No'}\n"
    return explanation
