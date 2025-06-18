import os, ast, json


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
    현재 폴더 기준으로 전체 구조를 탐색합니다.
    - __pycache__, .venv, .git, .idea, .gptcache 제외
    - .pyc 파일 제외
    """
    tree_lines = []

    for root, dirs, files in os.walk(base_path):
        # 📌 디렉토리 필터링
        dirs[:] = [
            d
            for d in dirs
            if d not in {"__pycache__", ".venv", "venv", ".git", ".idea", ".gptcache"}
        ]

        indent = "    " * (root[len(base_path) :].count(os.sep))
        tree_lines.append(f"{indent}📁 {os.path.basename(root)}/")

        for file in files:
            # 📌 파일 필터링: .py 파일만 허용 (.pyc, 기타 확장자 제외)
            if file.endswith(".py"):
                tree_lines.append(f"{indent}    📄 {file}")

    return "\n".join(tree_lines)


def extract_functions(root_dir):
    """_summary_

    Args:
        root_dir (_type_): _description_

    Returns:
        _type_: _description_
    """
    result = ""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # ✅ 무시할 디렉토리 추가
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {"__pycache__", ".venv", "venv", ".git", ".idea", ".gptcache"}
        ]

        for fname in filenames:
            if fname.endswith(".py"):
                path = os.path.join(dirpath, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    funcs = [
                        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    ]
                    if funcs:
                        rel_path = os.path.relpath(path, root_dir)
                        result += f"\n📄 {rel_path}\n"
                        for func in funcs:
                            doc = ast.get_docstring(func)
                            result += f"  - def {func.name}()\n"
                            if doc:
                                for line in doc.strip().splitlines():
                                    result += f"      {line.strip()}\n"
                except Exception as e:
                    result += f"\n[⚠️ Error parsing {fname}: {e}]\n"
    return result


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
