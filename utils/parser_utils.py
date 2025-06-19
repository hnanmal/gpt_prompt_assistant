import os, ast, json
from pyjsparser import PyJsParser


def summarize_functions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    lines = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            args = ", ".join(arg.arg for arg in node.args.args)
            doc = ast.get_docstring(node) or "(설명 없음)"
            lines.append(f"🔹 {name}({args})\n    {doc.strip()}\n")

    return "\n".join(lines) or "요약할 함수가 없습니다."


def get_project_tree(base_path):
    """
    전체 프로젝트 폴더 구조를 반환합니다.
    - 특정 폴더 및 확장자 제외
    """
    tree_lines = []
    ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}

    for root, dirs, files in os.walk(base_path):
        print(f"📁 {root} -> 파일 수: {len(files)}")  # ← 파일 수 확인
        dirs[:] = [
            d
            for d in dirs
            if d not in {"__pycache__", ".venv", "venv", ".git", ".idea", ".gptcache"}
        ]

        indent = "    " * (root[len(base_path) :].count(os.sep))
        tree_lines.append(f"{indent}📁 {os.path.basename(root)}/")

        for file in sorted(files):
            ext = os.path.splitext(file)[1]
            if ext in ALLOWED_EXTENSIONS:
                tree_lines.append(f"{indent}    📄 {file}")

    return "\n".join(tree_lines)


def extract_functions(root_dir):
    """
    프로젝트 디렉토리 내 .py 및 .js 파일에서 함수 요약 추출
    """
    result = ""
    parser = PyJsParser()
    allowed_extensions = {".py", ".js"}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 📌 무시할 디렉토리
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {"__pycache__", ".venv", "venv", ".git", ".idea", ".gptcache"}
        ]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in allowed_extensions:
                continue

            path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(path, root_dir)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Python 파일 처리
                if ext == ".py":
                    tree = ast.parse(content)
                    funcs = [
                        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    ]
                    if funcs:
                        result += f"\n📄 {rel_path}\n"
                        for func in funcs:
                            doc = ast.get_docstring(func)
                            result += f"  - def {func.name}()\n"
                            if doc:
                                for line in doc.strip().splitlines():
                                    result += f"      {line.strip()}\n"

                # JavaScript 파일 처리
                elif ext == ".js":
                    parsed = parser.parse(content)
                    functions = []
                    for stmt in parsed.get("body", []):
                        if stmt["type"] == "FunctionDeclaration":
                            functions.append(stmt["id"]["name"])
                    if functions:
                        result += f"\n📄 {rel_path}\n"
                        for func_name in functions:
                            result += f"  - function {func_name}()\n"

            except Exception as e:
                result += f"\n[⚠️ Error parsing {rel_path}: {e}]\n"

    return result or "⚠️ 함수 요약 결과가 없습니다."


# def extract_functions(root_dir):
#     result = ""
#     for dirpath, dirnames, filenames in os.walk(root_dir):
#         # ✅ 무시할 디렉토리 추가
#         dirnames[:] = [
#             d
#             for d in dirnames
#             if d not in {"__pycache__", ".venv", "venv", ".git", ".idea", ".gptcache"}
#         ]

#         for fname in filenames:
#             if fname.endswith(".py"):
#                 path = os.path.join(dirpath, fname)
#                 try:
#                     with open(path, "r", encoding="utf-8") as f:
#                         tree = ast.parse(f.read())
#                     funcs = [
#                         n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
#                     ]
#                     if funcs:
#                         rel_path = os.path.relpath(path, root_dir)
#                         result += f"📄 {rel_path}\n"
#                         for func in funcs:
#                             doc = ast.get_docstring(func)
#                             summary = doc.split("\n")[0] if doc else ""
#                             result += f"  - def {func.name}() → {summary}\n"
#                 except:
#                     pass
#     return result


def load_config(project_root):
    config_path = os.path.join(project_root, "project.gptconfig.json")
    if not os.path.exists(config_path):
        return "(설정 파일 없음)"
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = f"- 디자인 패턴: {data.get('design_pattern', '없음')}\n- 주요 함수:"
    for k, v in data.get("function_list", {}).items():
        result += f"\n  - {k} → {v}"
    return result
