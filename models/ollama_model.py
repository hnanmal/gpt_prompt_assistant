# src/models/ollama_model.py


class OllamaModel:
    def __init__(self, name: str, speed_score: float = 0.0):
        self.name = name
        self.speed_score = speed_score

    def __repr__(self):
        return f"<OllamaModel name={self.name}, speed_score={self.speed_score}>"
