import os
import json
from utils.keyword_utils import extract_keywords
from utils.file_matcher import find_related_files
from utils.context_builder import infer_project_context
from models.project_model import ProjectContext
from utils.ollama_manager import apply_ollama_model, get_installed_models
from utils.parser_utils import get_project_tree, extract_functions


def initialize_model_on_start(viewmodel):
    installed_models = get_installed_models()
    if "phi3:mini" in installed_models:
        apply_ollama_model("phi3:mini")
        viewmodel.set_current_model("phi3:mini")
        print("기본 모델 'phi3:mini' 자동 적용됨.")
    else:
        print("'phi3:mini'가 설치되어 있지 않음.")


class PromptViewModel:
    def __init__(self):
        self.context = ProjectContext()
        self.cache_dir = None
        self.used_cache = False
        self.current_model = None
        self.last_ollama_result = None
        initialize_model_on_start(self)

    def set_current_model(self, model_name):
        self.current_model = model_name

    def get_current_model(self):
        return self.current_model

    def _ensure_cache_dir(self, folder_path):
        cache_path = os.path.join(folder_path, ".gptcache")
        os.makedirs(cache_path, exist_ok=True)
        self.cache_dir = cache_path
        return cache_path

    def _detect_code_root(self, folder_path):
        src_path = os.path.join(folder_path, "src")
        if os.path.exists(src_path):
            return src_path

        subdirs = [
            os.path.join(folder_path, d)
            for d in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, d))
        ]
        subdirs_with_py_count = sorted(
            subdirs,
            key=lambda d: sum(f.endswith(".py") for f in os.listdir(d)),
            reverse=True,
        )
        return subdirs_with_py_count[0] if subdirs_with_py_count else folder_path

    def load_project(self, folder_path, force_reload=False):
        src_path = os.path.join(folder_path, "src")
        target_path = src_path if os.path.exists(src_path) else folder_path

        self.context.project_path = folder_path
        self.context.code_root = target_path
        cache_path = self._ensure_cache_dir(folder_path)

        tree_path = os.path.join(cache_path, "structure.txt")
        func_path = os.path.join(cache_path, "functions.txt")
        config_path = os.path.join(cache_path, "config.txt")

        if not force_reload and all(
            map(os.path.exists, [tree_path, func_path, config_path])
        ):
            self.used_cache = True
            with open(tree_path, encoding="utf-8") as f:
                self.context.tree_structure = f.read()
            with open(func_path, encoding="utf-8") as f:
                self.context.function_summary = f.read()
            with open(config_path, encoding="utf-8") as f:
                self.context.config_summary = f.read()
        else:
            self.used_cache = False
            self.context.tree_structure = get_project_tree(target_path)
            self.context.function_summary = extract_functions(target_path)

            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    self.context.config_summary = f.read()
            else:
                inferred_config = infer_project_context(folder_path)
                self.context.config_summary = "\n".join(
                    f"- {k}: {v}" for k, v in inferred_config.items()
                )
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(self.context.config_summary)

            with open(tree_path, "w", encoding="utf-8") as f:
                f.write(self.context.tree_structure)
            with open(func_path, "w", encoding="utf-8") as f:
                f.write(self.context.function_summary)

        print("📂 구조 요약:", self.context.tree_structure[:100])
        print("🧠 함수 요약:", self.context.function_summary[:100])
        print("⚙️ 설정 요약:", self.context.config_summary[:100])

        return True, "프로젝트 로드 성공", self.used_cache

    # ✅ 스트리밍 중 받은 결과 최종 저장
    def set_last_ollama_result(self, result: str):
        self.last_ollama_result = result.strip()

    def get_last_ollama_result(self):
        return self.last_ollama_result or "(없음)"

    def generate_prompt(self, user_input):
        if not user_input:
            return "요청 내용을 입력하세요."

        keywords = extract_keywords(user_input)
        related_files = find_related_files(self.context.code_root, keywords)
        related_files_text = "\n".join(f"- {f}" for f in related_files[:5]) or "(없음)"

        context_info = self.context.config_summary or (
            "\n".join(
                f"- {k}: {v}"
                for k, v in infer_project_context(
                    self.context.project_path or "."
                ).items()
            )
        )

        prompt_parts = [
            f"### 🔧 프로젝트 컨텍스트\n{context_info or '(없음)'}",
            f"### 📁 프로젝트 구조\n{self.context.tree_structure or '(없음)'}",
            f"### 🤖 Ollama 분석 결과\n{self.get_last_ollama_result()}",
            f"### 📂 관련 파일 추천 (룰 기반)\n{related_files_text}",
            f"### 🗣️ 내 요청:\n{user_input}",
        ]

        return "\n\n".join(prompt_parts)

    def is_cache_used(self):
        return self.used_cache

    # 🔽 PromptViewModel 내부에 추가
    def build_stream_prompt(self, user_input: str) -> str:
        if not user_input:
            return "요청 내용을 입력하세요."

        context_info = self.context.config_summary or (
            "\n".join(
                f"- {k}: {v}"
                for k, v in infer_project_context(
                    self.context.project_path or "."
                ).items()
            )
        )

        prompt_parts = [
            f"### 🔧 프로젝트 컨텍스트\n{context_info or '(없음)'}",
            f"### 📁 프로젝트 구조\n{self.context.tree_structure or '(없음)'}",
            # f"### 🤖 Ollama 분석 결과\n{self.get_last_ollama_result()}",
            # f"### 📂 관련 파일 추천 (룰 기반)\n{related_files_text}",
            f"### 🗣️ 내 요청:\n{user_input}",
        ]

        return "\n\n".join(prompt_parts)


# ✅ 전역 인스턴스 추가
viewmodel = PromptViewModel()
