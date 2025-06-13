import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from ttkbootstrap import Style
from controllers.model_controller import ModelController
from viewmodels.prompt_viewmodel import PromptViewModel
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
        self.style = Style("cosmo")  # 예시 테마

        self.current_model_var = tk.StringVar(value="(선택 안됨)")

        self.viewmodel = PromptViewModel()
        self.model_controller = ModelController()

        self._setup_ui()

    def _setup_ui(self):
        # 1. 좌우 프레임 구성
        self.sidebar_frame, self.right_frame = build_main_layout(self)

        # 사이드
        setup_sidebar(self.sidebar_frame, self)

        # 2. 상단 프레임
        self.top_frame = build_top_frame(self.right_frame)

        # 🔹 상태 / 버튼 섹션 생성 (self.~~ 로 바인딩)
        status_widgets = build_status_section(
            self.top_frame,
            on_open_project=self.on_open_project,
            on_refresh=self.on_refresh,
        )
        self.select_button = status_widgets["select_button"]
        self.refresh_button = status_widgets["refresh_button"]
        self.cache_label = status_widgets["cache_label"]
        self.status_label = status_widgets["status_label"]

        # 🔹 Ollama 모델 제어 UI 추가
        setup_ollama_controls(self.top_frame, self)

        # 3. 입력 프레임 (Entry)
        self.input_entry = build_input_frame(self.right_frame)

        # 4. 출력 박스
        self.output_box = build_output_box(self.right_frame)

        # 5. 버튼 영역
        self.button_frame = build_button_frame(self.right_frame)

        # 예시 버튼
        self.run_button = tk.Button(self.button_frame, text="실행", command=self.on_run)
        self.run_button.pack()

    # 🔹 실제 핸들러 구현
    def on_open_project(self):
        file_path = filedialog.askopenfilename(
            title="프로젝트 파일 열기",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.output_box.insert("end", f"[열린 파일 내용]\n{content}\n")
                self.status_label.config(text=f"✅ 프로젝트 파일 열기 완료")
            except Exception as e:
                messagebox.showerror("오류", str(e))
                self.status_label.config(text="❌ 파일 열기 실패")

    def on_refresh(self):
        self.output_box.delete("1.0", "end")
        self.status_label.config(text="🔄 출력창 초기화 완료")

    def on_run(self):
        input_text = self.input_entry.get().strip()
        if not input_text:
            messagebox.showwarning("입력 없음", "먼저 입력란에 텍스트를 입력하세요.")
            return

        self.output_box.insert("end", f"👉 입력: {input_text}\n")

        try:
            # 예시: Ollama 호출 시뮬레이션
            response = self.model_controller.query_model(input_text)
            self.output_box.insert("end", f"🧠 응답: {response}\n\n")
            self.status_label.config(text="✅ 응답 생성 완료")
        except Exception as e:
            self.output_box.insert("end", f"[오류 발생] {str(e)}\n")
            self.status_label.config(text="❌ 오류 발생")

    def on_apply_model(self):
        selected = self.viewmodel.get_current_model()
        if not selected:
            messagebox.showwarning("모델 선택", "먼저 사용할 모델을 선택하세요.")
            return

        success = self.model_controller.apply_selected_model(selected)
        if success:
            self.status_label.config(text=f"✅ {selected} 모델 적용됨")
            self.current_model_var.set(selected)
        else:
            self.status_label.config(text="❌ 모델 적용 실패")

    def install_model_popup(self):
        model_name = simpledialog.askstring(
            "모델 설치", "설치할 모델 이름을 입력하세요:"
        )
        if model_name:
            from utils.ollama_manager import install_ollama_model

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
