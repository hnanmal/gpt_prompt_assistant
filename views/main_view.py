import threading
import tkinter as tk
from tkinter import messagebox

# import ttkbootstrap.themes

from ttkbootstrap import Style

from controllers.model_controller import ModelController
from controllers.project_controller import ProjectController
from viewmodels.prompt_viewmodel import viewmodel  # 전역 ViewModel

from views.layout_builder import (
    build_main_layout,
    build_top_frame,
)
from views.ollama_section import setup_ollama_controls, update_ollama_button
from controllers.popup_handlers import show_model_apply_result_popup
from views.sidebar_section import setup_sidebar
from views.status_section import build_status_section
from views.prompt_section import setup_prompt_controls  # ✅ 입출력 UI 통합
from views.menus import create_menubar


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPT Prompt Assistant")
        self.geometry("1200x800")
        self.style = Style("cosmo")

        # 메뉴 설정
        create_menubar(self, self.on_open_project)

        self.project_loaded = False
        self.viewmodel = viewmodel
        self.model_controller = ModelController()
        self.project_controller = ProjectController(self, self.viewmodel)

        self._setup_ui()
        self.update_current_model_label()

    def _setup_ui(self):
        self.sidebar_frame, self.right_frame = build_main_layout(self)
        setup_sidebar(self.sidebar_frame, self)

        self.top_frame = build_top_frame(self.right_frame)

        self.ollama_control_frame = tk.Frame(self.top_frame)
        self.ollama_control_frame.pack(fill="x", expand=True)
        setup_ollama_controls(self.ollama_control_frame, self)

        self.status_frame = tk.Frame(self.top_frame)
        self.status_frame.pack(fill="x", expand=True)

        status_widgets = build_status_section(
            self.status_frame,
            on_open_project=self.on_open_project,
            on_refresh=self.on_refresh,
        )
        self.select_button = status_widgets["select_button"]
        self.refresh_button = status_widgets["refresh_button"]
        self.cache_label = status_widgets["cache_label"]
        self.status_label = status_widgets["status_label"]

        # ✅ 입력/출력 프롬프트 영역 구성 (prompt_section.py에서 분리 관리)
        setup_prompt_controls(self.right_frame, self)

        self.update_current_model_label()

    def on_open_project(self):
        self.project_controller.select_project()

    def on_refresh(self):
        self.project_controller.reload_project()
        update_ollama_button(self)

    def start_ollama_status_thread(self):
        def check_loop():
            import time

            while True:
                self.after(0, lambda: update_ollama_button(self))
                time.sleep(10)

        threading.Thread(target=check_loop, daemon=True).start()

    def update_current_model_label(self):
        current = self.viewmodel.get_current_model()
        if current:
            self.status_label.config(text=f"GPT 상태: ✅ ({current})")
        else:
            self.status_label.config(text="GPT 상태: ❌")

    def on_apply_model(self):
        selected = self.model_var.get()
        if not selected:
            messagebox.showwarning("모델 선택", "먼저 사용할 모델을 선택하세요.")
            return

        self.model_controller.selected_model = next(
            (m for m in self.model_controller.models if m.name == selected), None
        )

        success = self.model_controller.apply_selected_model(selected)
        if success:
            self.update_current_model_label()
        else:
            self.status_label.config(text="❌ 모델 적용 실패")
        show_model_apply_result_popup(selected, success)

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
