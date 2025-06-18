import tkinter as tk


from views.main_view import MainView
from utils.ollama_manager import is_ollama_running, start_ollama_model_background

# from viewmodels.prompt_viewmodel import viewmodel, initialize_model_on_start
import threading
from tkinter import messagebox


def check_and_prompt_ollama(model="phi3:mini"):
    if not is_ollama_running():

        def prompt():
            answer = messagebox.askyesno(
                "Ollama 비활성화됨", "Ollama가 꺼져 있습니다. 실행하시겠습니까?"
            )
            if answer:
                start_ollama_model_background(model)

        # UI가 다 뜬 후 메시지 띄우도록 딜레이
        app.after(1000, prompt)


if __name__ == "__main__":
    # initialize_model_on_start(viewmodel)
    app = MainView()
    # Ollama 비동기 상태 체크 (UI 띄운 후 실행)
    threading.Thread(target=check_and_prompt_ollama, daemon=True).start()

    app.mainloop()
