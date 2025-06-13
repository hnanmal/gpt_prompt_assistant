import tkinter.ttk as ttk


def build_status_section(parent, on_open_project, on_refresh):
    """
    프로젝트 열기 버튼, 새로고침 버튼, 캐시 상태 라벨, 상태 라벨을 포함한 섹션을 생성합니다.
    """

    frame = ttk.Frame(parent)
    frame.pack(fill="x", padx=10, pady=(0, 5))

    select_button = ttk.Button(frame, text="📁 프로젝트 열기", command=on_open_project)
    select_button.pack(side="left", padx=(0, 5))

    refresh_button = ttk.Button(frame, text="🔄 새로고침", command=on_refresh)
    refresh_button.pack(side="left", padx=(0, 5))

    cache_label = ttk.Label(frame, text="❓ 캐시 상태 미정")
    cache_label.pack(side="left", padx=(10, 0))

    status_label = ttk.Label(frame, text="GPT 상태: ❌")
    status_label.pack(side="right")

    return {
        "frame": frame,
        "select_button": select_button,
        "refresh_button": refresh_button,
        "cache_label": cache_label,
        "status_label": status_label,
    }
