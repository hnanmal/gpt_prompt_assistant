# views/ollama_section.py

import threading
import tkinter as tk
from ttkbootstrap import ttk
from tkinter import messagebox

from utils.ollama_manager import (
    is_ollama_running,
    start_ollama_model_background,
    stop_ollama_process,
)


def setup_ollama_controls(parent, app):
    """
    Ollama 상태 버튼, 모델 선택, 설치, 적용 관련 위젯 생성
    :param parent: top_frame or 다른 프레임
    :param app: MainView 인스턴스 (상호작용 위함)
    """
    # Ollama 상태 버튼
    app.ollama_button = tk.Button(
        parent, text="🔄 Ollama 상태 확인 중...", command=lambda: toggle_ollama(app)
    )
    app.ollama_button.pack(side="left", padx=10)
    update_ollama_button(app)  # 초기 상태 반영

    # 모델 드롭다운
    app.model_var = tk.StringVar()
    app.model_dropdown = ttk.Combobox(app, textvariable=app.model_var, state="readonly")
    app.model_dropdown.pack(pady=5)

    # 모델 적용 버튼
    app.apply_model_btn = ttk.Button(app, text="모델 적용", command=app.on_apply_model)
    app.apply_model_btn.pack(pady=5)

    # 모델 설치 버튼
    app.install_model_button = ttk.Button(
        app, text="모델 설치", command=app.install_model_popup
    )
    app.install_model_button.pack(pady=5)

    # 현재 모델 상태 라벨
    app.current_model_label = tk.Label(
        parent,
        textvariable=app.current_model_var,
        font=("맑은 고딕", 10, "bold"),
        fg="#333333",
    )
    app.current_model_label.pack(side="right", padx=10)


def update_ollama_status(app):
    def check_status():
        running = is_ollama_running()
        app.after(
            0,
            lambda: app.submit_button.config(state="normal" if running else "disabled"),
        )

    threading.Thread(target=check_status, daemon=True).start()


def update_ollama_button(app):
    def check_and_update():
        running = is_ollama_running()
        label = "🟢 Ollama 실행 중" if running else "🔴 Ollama 꺼짐"
        app.after(0, lambda: app.ollama_button.config(text=label))

    threading.Thread(target=check_and_update, daemon=True).start()


def toggle_ollama(app):
    if is_ollama_running():
        confirm = messagebox.askyesno("Ollama 종료", "Ollama를 종료하시겠습니까?")
        if confirm:
            success = stop_ollama_process()
            if success:
                messagebox.showinfo("종료 완료", "Ollama가 종료되었습니다.")
            else:
                messagebox.showwarning("종료 실패", "Ollama를 종료할 수 없습니다.")
    else:
        confirm = messagebox.askyesno("Ollama 실행", "Ollama를 실행하시겠습니까?")
        if confirm:
            model_name = app.viewmodel.selected_model.get()
            start_ollama_model_background(model_name)
            messagebox.showinfo(
                "Ollama 실행됨", "새 CMD 창에서 Ollama가 실행되었습니다."
            )

    update_ollama_status(app)
    update_ollama_button(app)
