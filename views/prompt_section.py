# views/prompt_section.py

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


def setup_prompt_controls(parent, app):
    """
    입력창, 제출 버튼, 출력창, 하단 버튼들(UI) 구성
    :param parent: 오른쪽 프레임 (right_frame)
    :param app: MainView 인스턴스
    """
    # 입력창
    app.input_entry = tk.Entry(parent, width=80)
    app.input_entry.pack(padx=10, pady=5, fill="x")
    app.input_entry.bind("<Return>", lambda event: on_user_submit(app))

    # 제출 버튼
    app.submit_button = tk.Button(
        parent, text="✉️ 요청 보내기", command=lambda: on_user_submit(app)
    )
    app.submit_button.pack(pady=5)

    # 출력창
    app.output_box = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=30)
    app.output_box.pack(padx=10, pady=(5, 0), fill="both", expand=True)

    # 버튼 프레임
    button_frame = tk.Frame(parent)
    button_frame.pack(padx=10, pady=(2, 10), anchor="e")

    app.copy_button = tk.Button(
        button_frame, text="📋 복사", command=lambda: copy_output(app)
    )
    app.copy_button.pack(side="left", padx=5)

    app.save_button = tk.Button(
        button_frame, text="💾 저장", command=lambda: save_output(app)
    )
    app.save_button.pack(side="left", padx=5)

    app.func_summary_button = tk.Button(
        button_frame,
        text="🧠 함수 요약 보기",
        command=lambda: show_function_summary_popup(app),
    )
    app.func_summary_button.pack(side="left", padx=5)


def on_user_submit(app):
    user_input = app.input_entry.get()
    if not app.project_loaded:
        messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
        return

    app.status_label.config(text="⏳ GPT 응답 대기 중...")
    app.submit_button.config(state="disabled")
    app.output_box.delete("1.0", tk.END)

    threading.Thread(
        target=lambda: run_gpt_prompt_thread(app, user_input), daemon=True
    ).start()


def run_gpt_prompt_thread(app, user_input):
    result = app.viewmodel.generate_prompt(user_input)
    app.after(0, lambda: update_output(app, result))


def update_output(app, result):
    app.output_box.insert(tk.END, result)
    app.status_label.config(text="✅ 완료")
    app.submit_button.config(state="normal")
    app.show_custom_toast("프롬프트 생성이 완료되었습니다.")


def copy_output(app):
    text = app.output_box.get("1.0", tk.END).strip()
    if text:
        app.clipboard_clear()
        app.clipboard_append(text)
        app.update()


def save_output(app):
    text = app.output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("경고", "저장할 내용이 없습니다.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="결과 저장",
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("저장 완료", f"결과가 저장되었습니다:\n{file_path}")


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
