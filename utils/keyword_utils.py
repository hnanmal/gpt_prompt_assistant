import re

# 자주 등장하지만 의미 없는 단어들 (불용어)
COMMON_STOPWORDS = {
    "을", "를", "이", "가", "은", "는", "에", "에서", "으로", "로",
    "해줘", "해라", "하기", "중", "같은", "있는", "해", "줘", "좀", "해줘요"
}

def extract_keywords(text: str) -> list[str]:
    """
    사용자의 요청 문장에서 의미 있는 키워드만 추출한다.
    한글/영어 단어 위주로 처리하며, 2글자 이상 + 불용어 제거
    """
    # 영어와 한글 단어 추출
    tokens = re.findall(r"[가-힣a-zA-Z]{2,}", text.lower())
    # 불용어 제거 및 중복 제거
    keywords = [t for t in tokens if t not in COMMON_STOPWORDS]
    return list(set(keywords))
