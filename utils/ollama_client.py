import json
import ollama
import requests


def ask_ollama(prompt: str, model="mistral") -> str:
    """
    Ollama 모델에게 프롬프트를 보내고 응답을 받아 반환
    """
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def ask_ollama_stream(model, prompt, on_token_callback, on_complete_callback):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt":
        #     """
        # [답변 시 지켜야 할 규칙]
        # 프로젝트 파일 중 '내 요청'과 관계된 것만 반드시 파일이름만 목록을 만들어서 대답해줘.
        # 제발 파일 이름만 불러주고 끝내. 답변이 총 200자를 넘지마.
        # 내 요청에 직접 대답하는 것이 아니야. 내 요청을 수행하기 위해 관련되어 보이는 파일만 고르면 돼.
        # 파일이름은 반드시 '프로젝트 구조'로 준 목록에 있는 것들만 제시해.
        # 파일이름 목록 외에 자세한 설명은 전혀 할 필요 없어.
        # 이 밑에 나오는 정보는 참고용이야.
        # """
        """
        [Rules to Follow When Responding]  
        Only list the filenames that are *directly related* to my request from the project files.  
        Please, just list the filenames—nothing more. Do **not** exceed 200 characters in total.  
        Do **not** answer my request directly. Just select the files that *seem relevant* to perform the request.  
        Only choose filenames from the ones provided in the "Project Structure" list.  
        Do **not** include any explanations beyond the filename list.
        The information below is just for reference.\n
        """
        + prompt,
        "stream": True,
    }
    full_response = ""

    try:
        print("🔁 요청 시작:", prompt[:50])
        with requests.post(url, json=payload, stream=True, timeout=30) as response:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("response", "")
                    full_response += token
                    on_token_callback(token)
        print("✅ 스트림 응답 완료")

        # ✅ 모든 응답 완료 후 호출
        on_complete_callback(full_response.strip())
    except Exception as e:
        on_complete_callback(f"[오류 발생] {e}")
