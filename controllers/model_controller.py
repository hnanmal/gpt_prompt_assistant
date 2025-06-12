# src/controllers/model_controller.py

import subprocess
from models.ollama_model import OllamaModel
from utils.ollama_manager import (
    list_ollama_models,
    apply_ollama_model,
    start_ollama_model_background,
    stop_ollama_process,
)


class ModelController:
    def __init__(self):
        self.models = []
        self.selected_model = None

    def load_models(self):
        names = list_ollama_models()  # 예: ['llama3', 'mistral', ...]
        print(names)
        self.models = [OllamaModel(name) for name in names]
        return self.models

    def select_fastest_model(self):
        # TODO: 실제 속도 테스트 후 정렬
        if self.models:
            self.selected_model = self.models[0]  # 임시로 첫 번째 선택
        return self.selected_model

    # def apply_selected_model(self):
    #     if not self.selected_model:
    #         return False
    #     try:
    #         # 예시: 현재 실행 중인 ollama 모델을 종료하고 새로운 모델 실행
    #         stop_ollama_process()
    #         start_ollama_model_background(self.selected_model.name)
    #         return True
    #     except Exception as e:
    #         print(f"[모델 적용 실패]: {e}")
    #         return False

    def apply_selected_model(self, name: str):
        model = next((m for m in self.models if m.name == name), None)

        if model is None:
            print(f"[모델 적용 실패]: '{name}' 모델을 찾을 수 없습니다.")
            return False

        try:
            args = ["ollama", "run", model.name]
            subprocess.run(args, check=True)
            print(f"[모델 적용 성공]: {model.name}")
            return True
        except Exception as e:
            print(f"[모델 적용 실패]: {e}")
            return False
