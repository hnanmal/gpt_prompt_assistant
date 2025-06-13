# views/popup_handlers.py

import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import ttk
import subprocess


def show_function_summary_popup(app):
    summary = app.viewmodel.context.function_summary.strip()
    if not summary:
        messagebox.showinfo("알림", "함수 요약 정보가 없습니다.")
        return

    popup = tk.Toplevel(app)
    popup.title("🧠 함수 요약 보기")
    popup.geometry("800x600")
    popup.transient(app)

    text = tk.Text(popup, wrap="word", font=("Consolas", 10))
    text.insert("1.0", summary)
    text.config(state="disabled")

    scrollbar = tk.Scrollbar(popup, command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    text.pack(fill="both", expand=True)


def install_model_popup(app):
    popup = tk.Toplevel(app)
    popup.title("모델 설치")
    popup.geometry("300x150")
    popup.transient(app)

    label = tk.Label(
        popup,
        text="설치할 모델 이름을 입력하세요 (예: llama2)",
        font=("맑은 고딕", 10),
    )
    label.pack(pady=10)

    model_entry = tk.Entry(popup)
    model_entry.pack(pady=5)

    def install_and_close():
        model_name = model_entry.get().strip()
        if model_name:
            run_model_install_cmd(model_name)
        popup.destroy()

    install_btn = ttk.Button(popup, text="설치", command=install_and_close)
    install_btn.pack(pady=5)


def run_model_install_cmd(model_name: str):
    try:
        subprocess.Popen(
            ["cmd.exe", "/k", f"ollama pull {model_name}"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    except Exception as e:
        messagebox.showerror("오류", f"모델 설치 실패: {e}")
