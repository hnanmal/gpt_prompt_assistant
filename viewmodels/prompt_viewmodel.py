import os
from models.project_model import ProjectContext
from utils.parser_utils import get_project_tree, extract_functions, load_config
from utils.keyword_utils import extract_keywords
from utils.file_matcher import find_related_files

class PromptViewModel:
    def __init__(self):
        self.context = ProjectContext()

    def load_project(self, folder_path):
        src_path = os.path.join(folder_path, "src")
        if not os.path.exists(src_path):
            return False, "src 폴더가 존재하지 않습니다."

        self.context.project_path = folder_path
        self.context.tree_structure = get_project_tree(src_path)
        self.context.function_summary = extract_functions(src_path)
        self.context.config_summary = load_config(folder_path)
        return True, "로드 성공"

    def generate_prompt(self, user_request):
        if not user_request:
            return "요청 내용을 입력하세요."

        # 1. 키워드 추출
        keywords = extract_keywords(user_request)

        # 2. 관련 파일 추천
        src_path = os.path.join(self.context.project_path, "src")
        related_files = find_related_files(src_path, keywords)
        related_files_text = "\n".join(f"- {f}" for f in related_files[:5]) if related_files else "(없음)"

        # 3. 프롬프트 구성
        return f"""### 🔧 프로젝트 컨텍스트
{self.context.config_summary}

### 📁 프로젝트 구조
{self.context.tree_structure}

### 📂 관련된 파일 (자동 추천)
{related_files_text}

### 🧠 함수 요약
{self.context.function_summary}

### 🗣️ 내 요청:
{user_request}
"""
