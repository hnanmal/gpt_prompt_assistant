import os
import ast
import re


def infer_project_context(folder_path):
    EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules"}
    language_set = set()
    file_count = 0
    notebook = False

    for root, dirs, files in os.walk(folder_path):
        # 디렉토리 제외
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".ipynb", ".js", ".ts", ".html", ".css"]:
                file_count += 1

                if ext == ".py":
                    language_set.add("Python")
                elif ext == ".ipynb":
                    notebook = True
                elif ext == ".js":
                    language_set.add("JavaScript")
                elif ext == ".html":
                    language_set.add("HTML")

    return {
        "language": ", ".join(sorted(language_set)) or "Unknown",
        "notebooks": notebook,
        "file_count": file_count,
        "js_detected": "JavaScript" in language_set,
        "html_detected": "HTML" in language_set,
        "python_detected": "Python" in language_set,
    }


def extract_functions_from_file(filepath: str) -> list[str]:
    """
    .py 파일에서 함수 정의 이름들을 추출합니다.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        return [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
    except Exception:
        return []


def extract_functions_from_js_file(filepath: str) -> list[str]:
    """
    .js 또는 .jsx 파일에서 함수 이름 추출 (function, arrow function, export default 등)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        patterns = [
            r"function\s+(\w+)\s*\(",  # function Foo(
            r"const\s+(\w+)\s*=\s*\(",  # const Foo = (
            r"const\s+(\w+)\s*=\s*function",  # const Foo = function
            r"export\s+default\s+function\s+(\w+)",  # export default function Foo
            r"export\s+function\s+(\w+)",  # export function Foo
        ]

        matches = []
        for pattern in patterns:
            matches += re.findall(pattern, content)

        return list(set(matches))  # 중복 제거
    except Exception:
        return []


def generate_structure_summary(root_path: str, max_depth: int = 3) -> str:
    """
    주어진 루트 경로로부터 폴더 및 파일 구조를 문자열로 요약합니다.
    __pycache__, .pyc, .venv, .git 등은 제외합니다.
    """
    summary_lines = []

    def walk(path, depth):
        if depth > max_depth:
            return
        try:
            entries = sorted(os.listdir(path))
        except Exception:
            return

        for entry in entries:
            full_path = os.path.join(path, entry)

            # ⛔ 무시할 디렉토리
            if os.path.isdir(full_path) and entry in {
                "__pycache__",
                ".git",
                ".venv",
                ".idea",
                ".gptcache",
            }:
                continue

            # ✅ 디렉토리 처리
            if os.path.isdir(full_path):
                prefix = "  " * depth
                summary_lines.append(f"{prefix}📁 {entry}/")
                walk(full_path, depth + 1)

            # ✅ 파일 처리 (.pyc 같은 건 무시)
            elif os.path.isfile(full_path) and not entry.endswith(".pyc"):
                prefix = "  " * depth
                summary_lines.append(f"{prefix}📄 {entry}")

    walk(root_path, 0)
    return "\n".join(summary_lines)


def combine_context(project_context: str, structure: str, functions: str) -> str:
    """
    프로젝트 설명 + 구조 요약 + 함수 요약을 하나의 프롬프트 컨텍스트로 병합합니다.
    """
    return f"""### 🔧 프로젝트 컨텍스트
{project_context}

### 📁 프로젝트 구조
{structure}

### 🧠 함수 요약
{functions}
"""
