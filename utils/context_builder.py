import os
import ast
import re


def generate_structure_summary(root_path: str, max_depth: int = 3) -> str:
    """
    주어진 루트 경로로부터 폴더 및 파일 구조를 문자열로 요약합니다.
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
            prefix = "  " * depth
            if os.path.isdir(full_path):
                summary_lines.append(f"{prefix}📁 {entry}/")
                walk(full_path, depth + 1)
            elif os.path.isfile(full_path):
                summary_lines.append(f"{prefix}📄 {entry}")

    walk(root_path, 0)
    return "\n".join(summary_lines)


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


def generate_function_summary(
    root_path: str, include_exts: list[str] = [".py", ".js", ".jsx"]
) -> str:
    """
    주어진 루트 경로 내의 파일들에서 함수 정의를 찾아 요약합니다.
    """
    summary = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in include_exts):
                full_path = os.path.join(dirpath, filename)
                if filename.endswith(".py"):
                    functions = extract_functions_from_file(full_path)
                else:
                    functions = extract_functions_from_js_file(full_path)

                if functions:
                    rel_path = os.path.relpath(full_path, root_path)
                    summary.append(f"- {rel_path} :")
                    for fn in functions:
                        summary.append(f"  - {fn}()")
    return "\n".join(summary)


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
