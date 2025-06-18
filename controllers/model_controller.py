import subprocess
from models.ollama_model import OllamaModel
from viewmodels.prompt_viewmodel import viewmodel  # 전역 ViewModel
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
        print(f"[모델 목록 로드]: {names}")
        self.models = [OllamaModel(name) for name in names]
        return self.models

    def select_fastest_model(self):
        # TODO: 실제 속도 측정 로직 필요
        if self.models:
            self.selected_model = self.models[0]  # 우선 첫 번째 모델을 선택
        return self.selected_model

    def apply_selected_model(self, name: str):
        model = next((m for m in self.models if m.name == name), None)

        if model is None:
            print(f"[모델 적용 실패]: '{name}' 모델을 찾을 수 없습니다.")
            return False

        try:
            apply_ollama_model(model.name)
            print(f"[모델 적용 성공]: {model.name}")
            viewmodel.set_current_model(model.name)  # ✅ 성공한 경우만 적용

            return True
        except Exception as e:
            print(f"[Ollama 오류] 모델 적용 실패: {e}")
            return False
