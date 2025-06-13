# views/layout_builder.py

import tkinter as tk


def build_main_layout(parent):
    """
    전체 main_frame 내부의 좌/우 프레임을 나누고, 각각의 프레임을 반환합니다.
    """
    # 전체 main_frame
    main_frame = tk.Frame(parent)
    main_frame.pack(fill="both", expand=True)

    # 좌측: 사이드바 프레임
    sidebar_frame = tk.Frame(main_frame, width=300)
    sidebar_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

    # 우측: 우측 패널 프레임
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True)

    return sidebar_frame, right_frame


def build_top_frame(parent):
    """
    rigth_frame을 받아서, 그 하위에 top_frame을 생성, 반환합니다.
    """
    top_frame = tk.Frame(parent)
    top_frame.pack(padx=10, pady=5, fill="x")
    return top_frame


def build_input_frame(parent):
    """
    rigth_frame을 받아서, 그 하위에 input_frame을 생성, 반환합니다.
    input_frame은 사용자가 입력하는 초안 프롬프트를 입력받는 역활.
    """
    entry = tk.Entry(parent, width=80)
    entry.pack(padx=10, pady=5, fill="x")
    return entry


def build_output_box(parent):
    """
    rigth_frame을 받아서, 그 하위에 output_frame을 생성, 반환합니다.
    output_frame을 사용자가 입력하는 초안 프롬프트를 Ollama 모델이 보강한 결과를 출력하는 역활.
    """
    output_box = tk.Text(parent, wrap="word", height=30)
    output_box.pack(padx=10, pady=(5, 0), fill="both", expand=True)
    return output_box


def build_button_frame(parent):
    """
    rigth_frame을 받아서, 그 하위에 button_frame을 생성, 반환합니다.
    copy_button, save_button, func_summary_button 이 이 프레임의 내포 대상.
    """
    button_frame = tk.Frame(parent)
    button_frame.pack(padx=10, pady=(2, 10), anchor="e")
    return button_frame
