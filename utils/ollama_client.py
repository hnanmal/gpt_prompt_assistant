import ollama


def ask_ollama(prompt: str, model="mistral") -> str:
    """
    Ollama 모델에게 프롬프트를 보내고 응답을 받아 반환
    """
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]
