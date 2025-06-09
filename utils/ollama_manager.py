import subprocess
import shutil
import psutil
import requests


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


def start_ollama_model_background(model="mistral"):
    try:
        subprocess.Popen(["start", "cmd", "/k", f"ollama run {model}"], shell=True)
        return True
    except Exception as e:
        print(f"[Ollama] 모델 실행 실패: {e}")
        return False


def stop_ollama_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = proc.info.get("name") or ""
            cmdline = proc.info.get("cmdline") or []

            if "ollama" in name.lower() or any(
                "ollama" in str(arg).lower() for arg in cmdline
            ):
                proc.terminate()
                proc.wait(timeout=5)
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False
