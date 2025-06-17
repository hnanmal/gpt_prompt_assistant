import json
import subprocess
import shutil
import psutil
import requests


def list_ollama_models(base_url="http://localhost:11434"):
    """
    현재 Ollama 서버에서 사용 가능한 모델 목록을 반환합니다.

    Returns:
        list[str]: 설치된 모델 이름 리스트
    """
    try:
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        data = response.json()

        # 모델 이름만 추출
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print(f"[Ollama 오류] 모델 목록 가져오기 실패: {e}")
        return []


def is_ollama_installed():
    return shutil.which("ollama") is not None


def is_ollama_running():
    try:
        response = requests.get("http://localhost:11434", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def is_model_ready(model="mistral"):
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        tags = response.json().get("models", [])
        return any(m["name"] == model for m in tags)
    except:
        return False


def pull_model_if_needed(model="mistral"):
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        return True
    except Exception as e:
        print(f"[Ollama] 모델 다운로드 실패: {e}")
        return False


# 현재 실행 중인 ollama 프로세스 종료
def stop_ollama_process():
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            name = proc.info.get("name")
            cmdline = proc.info.get("cmdline", [])

            if name and "ollama" in name.lower():
                proc.terminate()
                return True
            elif cmdline and any("ollama" in arg.lower() for arg in cmdline if arg):
                proc.terminate()
                return True
    except Exception as e:
        print(f"[오류] Ollama 프로세스 종료 중 예외 발생: {e}")
    return False


# 새로운 모델을 백그라운드로 실행
def start_ollama_model_background(model_name: str):
    try:
        print(f"[모델 실행] ollama run {model_name}")
        subprocess.Popen(
            ["ollama", "run", model_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[실행 실패] {e}")
        raise e


def apply_ollama_model(model_name: str, base_url="http://localhost:11434") -> bool:
    """
    주어진 모델을 Ollama 서버에서 적용(로드)합니다.

    Returns:
        bool: 성공 여부
    """

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model_name, "prompt": "Hello", "stream": False},
            timeout=5,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Ollama 오류] 모델 적용 실패: {e}")
        return False


def get_installed_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            models = []
            for line in lines[1:]:  # 첫 줄은 헤더이므로 제외
                model_name = line.split()[0]  # 공백 기준 첫 번째 항목
                models.append(model_name)
            return models
        else:
            print("ollama list 실행 실패:", result.stderr)
            return []
    except Exception as e:
        print("오류 발생:", e)
        return []


def install_ollama_model(model_name: str):
    """
    주어진 모델 이름으로 ollama 모델을 설치합니다.
    새로운 콘솔 창에서 실행됩니다.
    """
    try:
        subprocess.Popen(
            ["cmd.exe", "/k", f"ollama pull {model_name}"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    except Exception as e:
        print(f"[오류] 모델 설치 실패: {e}")
