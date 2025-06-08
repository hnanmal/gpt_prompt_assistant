class ProjectContext:
    def __init__(self):
        self.project_path = ""
        self.tree_structure = ""
        self.function_summary = ""
        self.config_summary = ""

    def is_loaded(self):
        return self.project_path != ""