# controllers/project_controller.py

import tkinter as tk
from tkinter import filedialog, messagebox
from viewmodels.prompt_viewmodel import PromptViewModel
from views.sidebar_section import update_tree_structure


class ProjectController:
    def __init__(self, view: tk.Tk, viewmodel: PromptViewModel):
        self.view = view
        self.viewmodel = viewmodel

    def select_project(self):
        folder = filedialog.askdirectory(title="프로젝트 폴더 선택")
        if folder:
            success, msg, used_cache = self.viewmodel.load_project(folder)
            self._update_cache_label(used_cache)

            if success:
                self.view.project_loaded = True
                update_tree_structure(self.view)
                messagebox.showinfo("로드 완료", msg)
            else:
                messagebox.showerror("로드 실패", msg)

    def reload_project(self):
        if not self.view.project_loaded:
            messagebox.showwarning("경고", "먼저 프로젝트를 열어주세요.")
            return

        success, msg, used_cache = self.viewmodel.load_project(
            self.viewmodel.context.project_path, force_reload=True
        )
        self._update_cache_label(used_cache)

        if success:
            update_tree_structure(self.view)
            messagebox.showinfo(
                "✅ 새로고침 완료", "프로젝트 정보를 새로 분석하고 캐시를 갱신했습니다."
            )
        else:
            messagebox.showerror("❌ 새로고침 실패", msg)

    def _update_cache_label(self, used_cache: bool):
        label = "✅ 캐시 사용됨" if used_cache else "❌ 캐시 미사용"
        self.view.cache_label.config(text=label)
