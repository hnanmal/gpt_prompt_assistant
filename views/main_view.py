import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap import Style


from viewmodels.prompt_viewmodel import PromptViewModel


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
        success, msg, used_cache = self.viewmodel.load_project(
            self.viewmodel.context.project_path, force_reload=True
        )
        self.cache_label.config(
            text=f"{'✅ 캐시 사용됨' if used_cache else '❌ 캐시 미사용'}"
        )
        if success:
            self.update_tree_structure()
        messagebox.showinfo("새로고침 완료", "프로젝트 캐시를 새로 생성했습니다.")

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

        # ✅ 토스트 메시지 띄우기
        toast = ToastNotification(
            title="프롬프트 생성 완료",
            message="GPT 응답이 완료되었습니다.",
            duration=7000,  # 3초 후 자동 종료
            alert=True,
            position=(self.winfo_x() + 100, self.winfo_y() + 100),
        )
        toast.show_toast()
