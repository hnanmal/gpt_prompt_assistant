import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from controllers.model_controller import ModelController
from controllers.project_controller import ProjectController
from viewmodels.prompt_viewmodel import PromptViewModel
from viewmodels.prompt_viewmodel import viewmodel  # 전역 ViewModel
from views.layout_builder import (
    build_main_layout,
    build_top_frame,
    build_input_frame,
    build_output_box,
    build_button_frame,
)
from views.ollama_section import setup_ollama_controls
from views.sidebar_section import setup_sidebar
from views.status_section import build_status_section


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPT Prompt Assistant")
        self.geometry("1200x800")
        self.style = Style("cosmo")

        # 상태 변수
        self.project_loaded = False

        # 핵심 로직 객체
        # self.viewmodel = PromptViewModel()
        self.viewmodel = viewmodel
        self.model_controller = ModelController()
        self.project_controller = ProjectController(self, self.viewmodel)

        # UI 구성
        self._setup_ui()

    def _setup_ui(self):
        # 1. 좌우 프레임 구성
        self.sidebar_frame, self.right_frame = build_main_layout(self)

        # 2. 사이드바 구성
        setup_sidebar(self.sidebar_frame, self)

        # 3. 상단 프레임 + 상태/버튼 구성
        self.top_frame = build_top_frame(self.right_frame)

        # ollama 프레임
        self.ollama_control_frame = tk.Frame(self.top_frame)
        self.ollama_control_frame.pack(fill="x", expand=True)

        # Ollama 제어 섹션
        setup_ollama_controls(self.ollama_control_frame, self)

        # status 프레임
        self.status_frame = tk.Frame(self.top_frame)
        self.status_frame.pack(fill="x", expand=True)

        # 상태 위젯
        status_widgets = build_status_section(
            self.status_frame,
            on_open_project=self.on_open_project,
            on_refresh=self.on_refresh,
        )
        self.select_button = status_widgets["select_button"]
        self.refresh_button = status_widgets["refresh_button"]
        self.cache_label = status_widgets["cache_label"]
        self.status_label = status_widgets["status_label"]

        # 5. 입력창
        self.input_entry = build_input_frame(self.right_frame)
        self.input_entry.bind("<Return>", self.on_user_submit)

        self.submit_button = tk.Button(
            self.right_frame, text="✉️ 요청 보내기", command=self.on_user_submit
        )
        self.submit_button.pack(padx=5)

        # 6. 출력박스
        self.output_box = build_output_box(self.right_frame)

        # 7. 하단 버튼 영역
        self.button_frame = build_button_frame(self.right_frame)

        self.copy_button = tk.Button(
            self.button_frame, text="📋 복사", command=self.copy_output
        )
        self.copy_button.pack(side="left", padx=5)

        self.save_button = tk.Button(
            self.button_frame, text="💾 저장", command=self.save_output
        )
        self.save_button.pack(side="left", padx=5)

        self.summary_button = tk.Button(
            self.button_frame, text="🧠 함수 요약", command=self.show_function_summary
        )
        self.summary_button.pack(side="left", padx=5)

        self.update_current_model_label()

    # === 📁 프로젝트 관련 ===
    def on_open_project(self):
        self.project_controller.select_project()

    def on_refresh(self):
        self.project_controller.reload_project()

    def update_tree_structure(self):
        self.tree_box.config(state="normal")
        self.tree_box.delete("1.0", tk.END)
        self.tree_box.insert("1.0", self.viewmodel.context.tree_structure or "(없음)")
        self.tree_box.config(state="disabled")

    def update_current_model_label(self):
        current = self.viewmodel.get_current_model()
        if current:
            self.status_label.config(text=f"GPT 상태: ✅ ({current})")
        else:
            self.status_label.config(text="GPT 상태: ❌")

    def show_function_summary(self):
        if not self.project_loaded:
            messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
            return

        summary = self.viewmodel.context.function_summary or "(요약 없음)"

        summary_window = tk.Toplevel(self)
        summary_window.title("함수 요약 결과")
        summary_window.geometry("800x600")

        from tkinter import scrolledtext

        text_widget = scrolledtext.ScrolledText(summary_window, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", summary)
        text_widget.config(state="disabled")

    # === 🧠 모델 적용 ===
    def on_apply_model(self):
        selected = self.model_var.get()
        if not selected:
            messagebox.showwarning("모델 선택", "먼저 사용할 모델을 선택하세요.")
            return

        # ✅ 선택한 모델을 controller에도 반영
        self.model_controller.selected_model = next(
            (m for m in self.model_controller.models if m.name == selected), None
        )

        success = self.model_controller.apply_selected_model(selected)
        if success:
            self.update_current_model_label()
        else:
            self.status_label.config(text="❌ 모델 적용 실패")

    def install_model_popup(self):
        import tkinter.simpledialog as simpledialog
        from utils.ollama_manager import install_ollama_model

        model_name = simpledialog.askstring(
            "모델 설치", "설치할 모델 이름을 입력하세요:"
        )
        if model_name:
            try:
                self.status_label.config(text=f"⏳ {model_name} 설치 중...")
                self.update()
                success = install_ollama_model(model_name)
                if success:
                    self.status_label.config(text=f"✅ {model_name} 설치 완료")
                else:
                    self.status_label.config(text=f"❌ {model_name} 설치 실패")
            except Exception as e:
                self.status_label.config(text=f"❌ 오류 발생: {e}")

    # === 🧾 입력/출력 관련 ===
    def on_user_submit(self, event=None):
        if not self.project_loaded:
            messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
            return

        user_input = self.input_entry.get()
        if not user_input.strip():
            return

        self.status_label.config(text="⏳ GPT 응답 대기 중...")
        self.output_box.delete("1.0", tk.END)
        self.submit_button.config(state="disabled")

        import threading

        threading.Thread(
            target=self._run_prompt, args=(user_input,), daemon=True
        ).start()

    def _run_prompt(self, user_input):
        result = self.viewmodel.generate_prompt(user_input)
        self.after(0, lambda: self._display_result(result))

    def _display_result(self, result):
        self.output_box.insert(tk.END, result)
        self.status_label.config(text="✅ 완료")
        self.submit_button.config(state="normal")

    def copy_output(self):
        text = self.output_box.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()

    def save_output(self):
        from tkinter import filedialog

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
