# 📁 controllers/menu_handlers.py

from tkinter import filedialog, messagebox
from controllers.popup_handlers import show_custom_about_popup
from core import app_info


# def open_project(app):
#     path = filedialog.askopenfilename(
#         title="프로젝트 열기",
#         filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
#     )
#     if path:
#         print(f"📂 선택한 파일: {path}")
#         # TODO: app.project_loader.load(path) 같은 로직 연결 필요


def save_result(app):
    result = app.output_box.get("1.0", "end").strip()
    if not result:
        messagebox.showwarning("경고", "저장할 결과가 없습니다.")
        return

    path = filedialog.asksaveasfilename(
        title="결과 저장",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(result)
        messagebox.showinfo("저장 완료", f"결과가 저장되었습니다:\n{path}")


def show_about(app):
    # messagebox.showinfo("About", app_info.ABOUT_TEXT)
    show_custom_about_popup(app, title="About", message=app_info.ABOUT_TEXT)


def show_version(app):
    messagebox.showinfo("Version", f"{app_info.APP_NAME} - v{app_info.VERSION}")
