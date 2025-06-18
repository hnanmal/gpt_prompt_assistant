# controllers/output_handler.py

from utils.ollama_client import ask_ollama_stream
from utils.keyword_utils import extract_keywords
from utils.file_matcher import find_related_files
from utils.context_builder import infer_project_context


def start_ollama_analysis(
    viewmodel, user_input, on_token_callback, on_complete_callback
):
    print("🚀 start_ollama_analysis 진입")
    if not user_input:
        on_complete_callback("요청 내용을 입력하세요.")
        return

    model = viewmodel.get_current_model()
    if not model:
        on_complete_callback("[오류] 현재 모델이 선택되지 않았습니다.")
        return

    result_accumulator = []

    def on_token(token):
        result_accumulator.append(token)
        on_token_callback(token)

    def on_done(*args, **kwargs):
        print("🔥 on_done 호출됨")
        result = "".join(result_accumulator)
        viewmodel.set_last_ollama_result(result)
        on_complete_callback(result)

    # 핵심: 전체 컨텍스트를 포함한 프롬프트 사용
    full_prompt = viewmodel.build_stream_prompt(user_input)

    ask_ollama_stream(
        model=model,
        prompt=full_prompt,  # ⬅️ 핵심 수정!
        on_token_callback=on_token,
        on_complete_callback=on_done,
        should_stop_callback=viewmodel.should_stop,
    )


# def start_ollama_analysis(
#     viewmodel, user_input, on_token_callback, on_complete_callback
# ):
#     print("🚀 start_ollama_analysis 진입")  # ← 이거 출력되는지 확인
#     if not user_input:
#         on_complete_callback("요청 내용을 입력하세요.")
#         return

#     model = viewmodel.get_current_model()
#     if not model:
#         on_complete_callback("[오류] 현재 모델이 선택되지 않았습니다.")
#         return

#     result_accumulator = []

#     def on_token(token):
#         result_accumulator.append(token)
#         on_token_callback(token)

#     def on_done(*args, **kwargs):
#         print("🔥 on_done 호출됨")
#         ollama_result = "".join(result_accumulator)
#         viewmodel.set_last_ollama_result(ollama_result)  # 🔥 스트림 결과 저장

#         keywords = extract_keywords(user_input)
#         related_files = find_related_files(viewmodel.context.code_root, keywords)
#         related_files_text = "\n".join(f"- {f}" for f in related_files[:5]) or "(없음)"

#         if viewmodel.context.config_summary:
#             context_info = viewmodel.context.config_summary
#         else:
#             inferred = infer_project_context(viewmodel.context.project_path or ".")
#             context_info = "\n".join(f"- {k}: {v}" for k, v in inferred.items())

#         prompt_parts = [
#             f"### 🔧 프로젝트 컨텍스트\n{context_info or '(없음)'}",
#             f"### 📁 프로젝트 구조\n{viewmodel.context.tree_structure or '(없음)'}",
#             f"### 🤖 Ollama 분석 결과\n{ollama_result}",
#             f"### 📂 관련 파일 추천 (룰 기반)\n{related_files_text}",
#             f"### 🗣️ 내 요청:\n{user_input}",
#         ]
#         final_prompt = "\n\n".join(prompt_parts)

#         on_complete_callback(final_prompt)

#     ask_ollama_stream(
#         model=model,
#         prompt=f"""
# 다음 요청 문장에서 관련된 기능, 컴포넌트, 모듈, 파일명을 추론해서 목록으로 알려줘.
# 없거나 모르겠는 건 '모름'이라고 해도 좋아.
# 요청: "{user_input}"
# """.strip(),
#         on_token_callback=on_token,
#         on_complete_callback=on_done,
#     )
