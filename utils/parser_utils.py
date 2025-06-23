import os, ast, json
from pyjsparser import PyJsParser
import subprocess


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


def extract_js_functions_esprima(filepath):
    try:
        print(f"🧪 JS 분석 대상 파일: {filepath}")
        output = subprocess.check_output(
            ["node", "extract_js_functions.js", filepath],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print("✅ Node 결과:\n", output)
        return output.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print("❌ Node 실행 오류:\n", e.output)
        return [f"[⚠️ JS 파싱 오류: {e.output.strip()}]"]
    except FileNotFoundError:
        print("❌ Node.js 실행파일(node)을 찾을 수 없습니다.")
        return ["[⚠️ Node.js not found]"]


def extract_functions(root_dir):
    result = ""
    allowed_extensions = {".py", ".js", ".jsx", ".ts", ".tsx"}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {".git", ".idea", "__pycache__", ".venv", "venv"}
        ]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in allowed_extensions:
                continue

            path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(path, root_dir)

            try:
                if ext == ".py":
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
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

                # elif ext == ".js":
                elif ext in allowed_extensions:
                    funcs = extract_js_functions_esprima(path)
                    if funcs:
                        result += f"\n📄 {rel_path}\n"
                        for name in funcs:
                            result += f"  - function {name}()\n"

            except Exception as e:
                result += f"\n[⚠️ Error parsing {rel_path}: {e}]\n"

    return result or "⚠️ 함수 요약 결과가 없습니다."


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
