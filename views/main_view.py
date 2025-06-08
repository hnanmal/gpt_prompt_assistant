import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from viewmodels.prompt_viewmodel import PromptViewModel

class PromptView:
    def __init__(self, root):
        self.vm = PromptViewModel()
        self.root = root
        self.root.title("GPT 프롬프트 생성기")
        self.root.geometry("1100x900")

        self.setup_ui()

    def setup_ui(self):
        tk.Button(self.root, text="📂 프로젝트 불러오기", command=self.load_project).pack(pady=5)

        tk.Label(self.root, text="📝 GPT에게 하고 싶은 말").pack()
        self.input_box = scrolledtext.ScrolledText(self.root, height=4)
        self.input_box.pack(fill="both", padx=10)

        tk.Label(self.root, text="📁 프로젝트 구조").pack()
        self.tree_text = scrolledtext.ScrolledText(self.root, height=10)
        self.tree_text.pack(fill="both", padx=10)

        tk.Label(self.root, text="🧠 함수 요약").pack()
        self.func_text = scrolledtext.ScrolledText(self.root, height=10)
        self.func_text.pack(fill="both", padx=10)

        tk.Label(self.root, text="📜 설정 요약").pack()
        self.config_text = scrolledtext.ScrolledText(self.root, height=5)
        self.config_text.pack(fill="both", padx=10)

        tk.Button(self.root, text="🔁 프롬프트 생성", command=self.generate_prompt).pack(pady=10)

        tk.Label(self.root, text="🧾 결과 프롬프트").pack()
        self.output_box = scrolledtext.ScrolledText(self.root, height=15)
        self.output_box.pack(fill="both", padx=10)

        tk.Button(self.root, text="📋 복사", command=self.copy_to_clipboard).pack(pady=5)

    def load_project(self):
        folder = filedialog.askdirectory()
        ok, msg = self.vm.load_project(folder)
        if not ok:
            messagebox.showerror("오류", msg)
            return
        self.tree_text.delete("1.0", tk.END)
        self.tree_text.insert(tk.END, self.vm.context.tree_structure)

        self.func_text.delete("1.0", tk.END)
        self.func_text.insert(tk.END, self.vm.context.function_summary)

        self.config_text.delete("1.0", tk.END)
        self.config_text.insert(tk.END, self.vm.context.config_summary)

    def generate_prompt(self):
        user_text = self.input_box.get("1.0", tk.END).strip()
        prompt = self.vm.generate_prompt(user_text)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, prompt)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_box.get("1.0", tk.END))
        self.root.update()
        messagebox.showinfo("복사 완료", "프롬프트가 복사되었습니다.")