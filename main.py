import tkinter as tk
from tkinter import messagebox
from views.main_view import MainView

# Ollama 상태 체크 유틸
from utils.ollama_manager import (
    is_ollama_installed,
    is_ollama_running,
    start_ollama_model,
)


def ensure_ollama_ready():
    if not is_ollama_installed():
        messagebox.showwarning(
            "Ollama 미설치",
            "🤖 GPT 분석 기능을 사용하려면 Ollama가 필요합니다.\n\n"
            "1. https://ollama.com/download 에서 Ollama를 설치한 후\n"
            "2. 앱을 다시 실행해주세요.",
        )
        return False

    if not is_ollama_running():
        started = start_ollama_model("mistral")
        if started:
            messagebox.showinfo(
                "Ollama 실행됨",
                "Ollama가 자동으로 실행되었습니다.\n잠시 후 GPT 기능이 활성화됩니다.",
            )
        else:
            messagebox.showwarning(
                "Ollama 실행 실패",
                "Ollama를 자동으로 실행할 수 없습니다.\n\n터미널에서 직접 다음을 실행해주세요:\n\n"
                "    ollama run mistral",
            )
    return True


if __name__ == "__main__":
    ensure_ollama_ready()

    app = MainView()
    app.mainloop()
