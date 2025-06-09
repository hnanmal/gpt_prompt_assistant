import os
import json
from utils.ollama_client import ask_ollama
from utils.keyword_utils import extract_keywords
from utils.file_matcher import find_related_files
from models.project_model import ProjectContext
from utils.parser_utils import get_project_tree, extract_functions, load_config


class PromptViewModel:
    def __init__(self):
        self.context = ProjectContext()
        self.cache_dir = None
        self.used_cache = False

    def _ensure_cache_dir(self, folder_path):
        cache_path = os.path.join(folder_path, ".gptcache")
        os.makedirs(cache_path, exist_ok=True)
        self.cache_dir = cache_path
        return cache_path

    def load_project(self, folder_path, force_reload=False):
        src_path = os.path.join(folder_path, "src")
        if not os.path.exists(src_path):
            return False, "src 폴더가 존재하지 않습니다.", False

        self.context.project_path = folder_path
        cache_path = self._ensure_cache_dir(folder_path)

        # 캐시 파일 경로
        tree_path = os.path.join(cache_path, "structure.json")
        func_path = os.path.join(cache_path, "functions.json")
        config_path = os.path.join(cache_path, "config.json")

        # 캐시 여부 결정
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
            self.context.tree_structure = get_project_tree(src_path)
            self.context.function_summary = extract_functions(src_path)
            self.context.config_summary = load_config(folder_path)

            # 캐시 저장
            with open(tree_path, "w", encoding="utf-8") as f:
                f.write(self.context.tree_structure)
            with open(func_path, "w", encoding="utf-8") as f:
                f.write(self.context.function_summary)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(self.context.config_summary)

        return True, "프로젝트 로드 성공", self.used_cache

    def generate_prompt(self, user_input):
        if not user_input:
            return "요청 내용을 입력하세요."

        # 1. Ollama 분석 요청
        ollama_prompt = f"""
        다음 요청 문장에서 관련된 기능, 컴포넌트, 모듈, 파일명을 추론해서 목록으로 알려줘.
        없거나 모르겠는 건 '모름'이라고 해도 좋아.
        요청: "{user_input}"
        """
        try:
            ollama_result = ask_ollama(ollama_prompt)
        except Exception as e:
            ollama_result = f"(Ollama 응답 실패: {e})"

        # 2. 키워드 기반 관련 파일 추론
        keywords = extract_keywords(user_input)
        src_path = os.path.join(self.context.project_path, "src")
        related_files = find_related_files(src_path, keywords)
        related_files_text = "\n".join(f"- {f}" for f in related_files[:5]) or "(없음)"

        # ✅ 로그 출력
        print("🔍 [파일 매칭 로그]")
        print(f"- 사용자 키워드: {keywords}")
        print(f"- 매칭된 파일 수: {len(related_files)}")
        for path in related_files:
            print(f"  • {path}")

        prompt_parts = [
            f"### 🔧 프로젝트 컨텍스트\n{self.context.config_summary or '(없음)'}",
            f"### 📁 프로젝트 구조\n{self.context.tree_structure or '(없음)'}",
        ]

        # 🧠 함수 요약이 존재할 때만 추가
        if self.context.function_summary and self.context.function_summary.strip():
            prompt_parts.append(f"### 🧠 함수 요약\n{self.context.function_summary}")

        prompt_parts.extend(
            [
                f"### 🤖 Ollama 분석 결과\n{ollama_result}",
                f"### 📂 관련 파일 추천 (룰 기반)\n{related_files_text}",
                f"### 🗣️ 내 요청:\n{user_input}",
            ]
        )

        return "\n\n".join(prompt_parts)

    def is_cache_used(self):
        return self.used_cache
