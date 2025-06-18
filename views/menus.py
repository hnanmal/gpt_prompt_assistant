# 📁 views/menus.py

import tkinter as tk
from controllers import menu_handlers


def create_menubar(app, open_handler):
    menubar = tk.Menu(app)

    # 📁 File 메뉴
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(
        label="📂 Open Project...",
        command=open_handler,
    )
    # file_menu.add_command(
    #     label="💾 Save Result As...",
    #     command=lambda: menu_handlers.save_result(app),
    # )

    file_menu.add_separator()
    file_menu.add_command(label="❌ Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # ❓ Help 메뉴
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="ℹ️ About", command=lambda: menu_handlers.show_about(app)
    )
    help_menu.add_command(
        label="🔢 Version", command=lambda: menu_handlers.show_version(app)
    )
    menubar.add_cascade(label="Help", menu=help_menu)

    app.config(menu=menubar)
