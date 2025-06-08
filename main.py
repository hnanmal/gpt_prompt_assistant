import tkinter as tk
from views.main_view import PromptView

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptView(root)
    root.mainloop()