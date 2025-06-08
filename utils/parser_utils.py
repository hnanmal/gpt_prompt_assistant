import os, ast, json

def get_project_tree(root_dir, indent=""):
    result = ""
    for entry in sorted(os.listdir(root_dir)):
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path):
            result += f"{indent}📁 {entry}/\n"
            result += get_project_tree(full_path, indent + "  ")
        elif os.path.isfile(full_path):
            result += f"{indent}📄 {entry}\n"
    return result


def extract_functions(root_dir):
    result = ""
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                path = os.path.join(dirpath, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    if funcs:
                        rel_path = os.path.relpath(path, root_dir)
                        result += f"📄 {rel_path}\n"
                        for func in funcs:
                            doc = ast.get_docstring(func)
                            summary = doc.split('\n')[0] if doc else ""
                            result += f"  - def {func.name}() → {summary}\n"
                except:
                    pass
    return result

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