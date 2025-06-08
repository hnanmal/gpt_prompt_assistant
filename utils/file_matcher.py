import os

def find_related_files(root_path: str, keywords: list[str]) -> list[str]:
    """
    키워드와 관련된 파일들을 src 하위에서 탐색하여 중요도 순으로 정렬해 반환.
    파일 경로가 키워드를 얼마나 많이 포함하는지를 기준으로 가중치를 계산.
    """
    matched_files = []

    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_path)
            rel_path_lower = rel_path.lower()

            # 키워드 포함 개수로 점수 계산
            score = sum(1 for kw in keywords if kw in rel_path_lower)

            if score > 0:
                matched_files.append((score, rel_path))

    # 점수 높은 순으로 정렬
    matched_files.sort(reverse=True)
    return [path for score, path in matched_files]
