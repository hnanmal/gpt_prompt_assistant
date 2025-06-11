import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from ttkbootstrap import Style
from utils.ollama_manager import (
    is_ollama_running,
    start_ollama_model_background,
    stop_ollama_process,
)
from win10toast_click import ToastNotifier
from viewmodels.prompt_viewmodel import PromptViewModel
from utils.parser_utils import summarize_functions


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        # ttkbootstrap 적용
        self.style = Style("cosmo")  # 예: cosmo, flatly, darkly 등 다양한 테마 가능

        self.title("GPT Prompt Assistant")
        self.geometry("900x700")

        self.viewmodel = PromptViewModel()
        self.project_loaded = False

        self.create_widgets()

        self.update_ollama_status()

    def show_system_toast(self, message: str):
        try:
            toaster = ToastNotifier()
            toaster.show_toast(
                "GPT Prompt Assistant",
                "프롬프트 생성이 완료되었습니다.",
                duration=7,
                icon_path=None,
                threaded=False,
            )
        except Exception as e:
            print(f"토스트 알림 실패: {e}")

    def show_custom_toast(self, message: str):
        def _show():
            toast = tk.Toplevel(self)
            toast.title("📢 알림")
            toast.geometry("300x100+100+100")
            toast.attributes("-topmost", True)
            toast.resizable(False, False)
            toast.configure(bg="white")

            label = tk.Label(toast, text=message, bg="white", font=("맑은 고딕", 10))
            label.pack(pady=10, padx=10)

            close_button = tk.Button(toast, text="닫기", command=toast.destroy)
            close_button.pack(pady=5)

            toast.mainloop()

        # 별도 쓰레드로 실행
        threading.Thread(target=_show, daemon=True).start()

    def update_ollama_status(self):
        """Ollama 상태에 따라 요청 버튼 활성화/비활성화"""
        if is_ollama_running():
            self.submit_button.config(state="normal")
        else:
            self.submit_button.config(state="disabled")

    def create_widgets(self):
        # 전체 프레임 (좌우 분할용)
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # 좌측: 프로젝트 구조 표시용
        sidebar_frame = tk.Frame(main_frame, width=300)
        sidebar_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        sidebar_label = tk.Label(
            sidebar_frame,
            text="📁 프로젝트 구조",
            anchor="w",
            font=("맑은 고딕", 11, "bold"),
        )
        sidebar_label.pack(anchor="w")

        self.tree_box = scrolledtext.ScrolledText(sidebar_frame, wrap=tk.WORD, width=40)
        self.tree_box.pack(fill="both", expand=True)
        self.tree_box.insert(tk.END, "(아직 로드되지 않음)")
        self.tree_box.config(state="disabled")

        # 우측: 기존 전체 UI
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # 상단 프레임
        top_frame = tk.Frame(right_frame)
        top_frame.pack(padx=10, pady=5, fill="x")

        # Ollama 실행 상태 표시 버튼
        self.ollama_button = tk.Button(
            top_frame, text="🔄 Ollama 상태 확인 중...", command=self.toggle_ollama
        )
        self.ollama_button.pack(side="left", padx=10)
        self.update_ollama_button()  # 초기 상태 반영

        self.select_button = tk.Button(
            top_frame, text="📁 프로젝트 열기", command=self.select_project
        )
        self.select_button.pack(side="left")

        self.refresh_button = tk.Button(
            top_frame, text="🔄 새로고침", command=self.reload_project
        )
        self.refresh_button.pack(side="left", padx=5)

        self.cache_label = tk.Label(top_frame, text="❓ 캐시 상태 미정")
        self.cache_label.pack(side="left", padx=10)

        self.status_label = tk.Label(top_frame, text="")
        self.status_label.pack(side="left", padx=10)

        self.input_entry = tk.Entry(right_frame, width=80)
        self.input_entry.pack(padx=10, pady=5, fill="x")
        self.input_entry.bind("<Return>", self.on_user_submit)

        self.submit_button = tk.Button(
            right_frame, text="✉️ 요청 보내기", command=self.on_user_submit
        )
        self.submit_button.pack(pady=5)

        self.output_box = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD, height=30
        )
        self.output_box.pack(padx=10, pady=(5, 0), fill="both", expand=True)

        button_frame = tk.Frame(right_frame)
        button_frame.pack(padx=10, pady=(2, 10), anchor="e")

        self.copy_button = tk.Button(
            button_frame, text="📋 복사", command=self.copy_output
        )
        self.copy_button.pack(side="left", padx=5)

        self.save_button = tk.Button(
            button_frame, text="💾 저장", command=self.save_output
        )
        self.save_button.pack(side="left", padx=5)

        self.func_summary_button = tk.Button(
            button_frame,
            text="🧠 함수 요약 보기",
            command=self.show_function_summary_popup,
        )
        self.func_summary_button.pack(side="left", padx=5)

    def copy_output(self):
        text = self.output_box.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()

    def save_output(self):
        text = self.output_box.get("1.0", tk.END).strip()
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

    def select_project(self):
        folder = filedialog.askdirectory(title="프로젝트 폴더 선택")
        if folder:
            success, msg, used_cache = self.viewmodel.load_project(folder)
            self.cache_label.config(
                text=f"{'✅ 캐시 사용됨' if used_cache else '❌ 캐시 미사용'}"
            )
            self.project_loaded = success
            if success:
                self.update_tree_structure()
            messagebox.showinfo("로드 결과", msg)

    def reload_project(self):
        if not self.project_loaded:
            messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
            return

        # 🔄 캐시 무시하고 강제 로드
        success, msg, used_cache = self.viewmodel.load_project(
            self.viewmodel.context.project_path, force_reload=True
        )

        # ✅ 캐시 상태 업데이트
        self.cache_label.config(
            text=f"{'✅ 캐시 사용됨' if used_cache else '❌ 캐시 미사용'}"
        )

        if success:
            self.update_tree_structure()
            messagebox.showinfo(
                "✅ 새로고침 완료", "프로젝트 정보를 새로 분석하고 캐시를 갱신했습니다."
            )
        else:
            messagebox.showerror("❌ 새로고침 실패", msg)

    def update_ollama_button(self):
        def check_and_update():
            running = is_ollama_running()
            label = "🟢 Ollama 실행 중" if running else "🔴 Ollama 꺼짐"
            self.ollama_button.config(text=label)

        threading.Thread(target=check_and_update, daemon=True).start()

    def toggle_ollama(self):
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
                start_ollama_model_background()
                messagebox.showinfo(
                    "Ollama 실행됨", "새 CMD 창에서 Ollama가 실행되었습니다."
                )

        self.update_ollama_status()
        self.update_ollama_button()

    def update_tree_structure(self):
        self.tree_box.config(state="normal")
        self.tree_box.delete("1.0", tk.END)
        self.tree_box.insert("1.0", self.viewmodel.context.tree_structure or "(없음)")
        self.tree_box.config(state="disabled")

    def on_user_submit(self, event=None):
        user_input = self.input_entry.get()
        if not self.project_loaded:
            messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
            return

        # 상태 표시: GPT 응답 대기 중
        self.status_label.config(text="⏳ GPT 응답 대기 중...")
        self.submit_button.config(state="disabled")
        self.output_box.delete("1.0", tk.END)

        # GPT 호출 스레드 시작
        threading.Thread(
            target=self.run_gpt_prompt_thread, args=(user_input,), daemon=True
        ).start()

    def run_gpt_prompt_thread(self, user_input):
        result = self.viewmodel.generate_prompt(user_input)

        # UI 업데이트는 메인 스레드에서 해야 함
        self.after(0, self.update_output, result)

    def update_output(self, result):
        self.output_box.insert(tk.END, result)
        self.status_label.config(text="✅ 완료")
        self.submit_button.config(state="normal")
        self.show_custom_toast("프롬프트 생성이 완료되었습니다.")

    def show_function_summary_popup(self):
        summary = self.viewmodel.context.function_summary.strip()
        if not summary:
            messagebox.showinfo("알림", "함수 요약 정보가 없습니다.")
            return

        popup = tk.Toplevel(self)
        popup.title("🧠 함수 요약 보기")
        popup.geometry("800x600")
        popup.transient(self)  # 부모 위에 떠 있게

        text = tk.Text(popup, wrap="word", font=("Consolas", 10))
        text.insert("1.0", summary)
        text.config(state="disabled")

        scrollbar = tk.Scrollbar(popup, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
