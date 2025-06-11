import os
import re

# 📌 Python 함수 파싱용
import ast

# ✅ 키워드 유사어 매핑
KEYWORD_VARIANTS = {
    "복사": ["copy", "duplicate", "clone", "복사"],
    "팝업": ["popup", "modal", "dialog", "alert", "팝업"],
    "트리": ["tree", "node", "branch", "leaf", "트리"],
    "버튼": ["button", "click", "press", "btn", "버튼"],
    "우측": ["right", "context", "우클릭", "rightclick", "우측"],
}


def expand_keywords(keywords):
    expanded = []
    for word in keywords:
        expanded.extend(KEYWORD_VARIANTS.get(word, [word]))
    return list(set(expanded))


def extract_function_bodies_from_python(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        return [
            (node.name, ast.get_source_segment(source, node))
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
    except Exception:
        return []


def extract_function_bodies_from_js(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        pattern = re.compile(
            r"(?:function\s+|const\s+)(\w+)\s*=\s*\(.*?\)\s*=>\s*{.*?}", re.DOTALL
        )
        matches = pattern.findall(source)
        return [(name, source) for name in matches]
    except Exception:
        return []


# def find_related_files(folder_path, keywords):
#     related = []
#     keywords = expand_keywords(keywords)

#     for root, _, files in os.walk(folder_path):
#         for file in files:
#             if not file.endswith((".py", ".js", ".jsx")):
#                 continue

#             full_path = os.path.join(root, file)
#             try:
#                 content = ""
#                 if file.endswith(".py"):
#                     functions = extract_function_bodies_from_python(full_path)
#                 else:
#                     functions = extract_function_bodies_from_js(full_path)

#                 content += "\n".join([body for _, body in functions])
#                 with open(full_path, "r", encoding="utf-8") as f:
#                     content += f.read()

#                 if any(kw.lower() in content.lower() for kw in keywords):
#                     related.append(os.path.relpath(full_path, folder_path))

#             except Exception:
#                 continue

#     return related

import os


EXCLUDED_DIRS = {".venv", "venv", "__pycache__", ".git", ".idea", ".gptcache"}
SUPPORTED_EXTS = [".py", ".js", ".jsx"]


def find_related_files(root_dir: str, keywords: list[str]) -> list[str]:
    matched_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 📌 제외할 디렉토리 필터링
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        for fname in filenames:
            # 📌 제외할 파일 확장자 필터링
            if not any(fname.endswith(ext) for ext in SUPPORTED_EXTS):
                continue

            # 📌 전체 경로
            full_path = os.path.join(dirpath, fname)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if any(keyword in content for keyword in keywords):
                        matched_files.append(os.path.relpath(full_path, root_dir))
            except Exception:
                continue

    return matched_files
