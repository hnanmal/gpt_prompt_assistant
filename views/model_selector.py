# from ttkbootstrap import ttk


# class ModelSelector(ttk.Frame):
#     def __init__(self, parent, controller, viewmodel):
#         super().__init__(parent)
#         self.controller = controller
#         self.viewmodel = viewmodel

#         # 모델 선택 콤보박스
#         self.combo = ttk.Combobox(self, textvariable=self.viewmodel.selected_model)
#         self.combo.pack(side="left", padx=5)

#         # 적용 버튼
#         ttk.Button(self, text="모델 적용", command=self.apply_model).pack(side="left")

#         self.load_models()

#     def load_models(self):
#         models = self.controller.get_model_names()
#         self.combo["values"] = models
#         if models:
#             self.viewmodel.selected_model.set(models[0])

#     def apply_model(self):
#         selected = self.viewmodel.selected_model.get()
#         if self.controller.apply_selected_model(selected):
#             toast("✅ 모델이 적용되었습니다.")
