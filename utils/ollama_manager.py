import subprocess
import requests


def is_ollama_installed() -> bool:
    """
    시스템에 ollama CLI가 설치되어 있는지 확인합니다.
    """
    try:
        subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def is_ollama_running() -> bool:
    """
    Ollama 서버가 실행 중인지 확인합니다.
    """
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except Exception:
        return False


def start_ollama_model(model: str = "mistral") -> bool:
    """
    Ollama 모델을 백그라운드에서 실행합니다.
    예: ollama run mistral
    """
    try:
        subprocess.Popen(
            ["ollama", "run", model],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False
