# views/sidebar_section.py

import tkinter as tk
from tkinter import scrolledtext


def setup_sidebar(parent, app):
    """
    프로젝트 구조 표시용 사이드바 UI 생성
    :param parent: main_frame
    :param app: MainView 인스턴스
    :return: 사이드바 프레임
    """
    sidebar_frame = tk.Frame(parent, width=300)
    sidebar_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

    sidebar_label = tk.Label(
        sidebar_frame,
        text="📁 프로젝트 구조",
        anchor="w",
        font=("맑은 고딕", 11, "bold"),
    )
    sidebar_label.pack(anchor="w")

    app.tree_box = scrolledtext.ScrolledText(sidebar_frame, wrap=tk.WORD, width=40)
    app.tree_box.pack(fill="both", expand=True)
    app.tree_box.insert("1.0", "(아직 로드되지 않음)")
    app.tree_box.config(state="disabled")

    return sidebar_frame


def update_tree_structure(app):
    """
    ViewModel의 context로부터 프로젝트 트리 문자열을 불러와 출력창 갱신
    """
    app.tree_box.config(state="normal")
    app.tree_box.delete("1.0", tk.END)
    app.tree_box.insert("1.0", app.viewmodel.context.tree_structure or "(없음)")
    app.tree_box.config(state="disabled")
