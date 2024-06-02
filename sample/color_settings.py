import json
import tkinter as tk
from tkinter import ttk

# ANSI 색상 코드와 RGB 색상 매핑
ansi_colors = {
    "black": ('\033[0;30m', '#000000'),
    "red": ('\033[0;31m', '#ff0000'),
    "green": ('\033[0;32m', '#00ff00'),
    "yellow": ('\033[0;33m', '#ffff00'),
    "blue": ('\033[0;34m', '#0000ff'),
    "magenta": ('\033[0;35m', '#ff00ff'),
    "cyan": ('\033[0;36m', '#00ffff'),
    "white": ('\033[0;37m', '#ffffff'),
    "bright_black": ('\033[0;90m', '#808080'),
    "bright_red": ('\033[0;91m', '#ff8080'),
    "bright_green": ('\033[0;92m', '#80ff80'),
    "bright_yellow": ('\033[0;93m', '#ffff80'),
    "bright_blue": ('\033[0;94m', '#8080ff'),
    "bright_magenta": ('\033[0;95m', '#ff80ff'),
    "bright_cyan": ('\033[0;96m', '#80ffff'),
    "bright_white": ('\033[0;97m', '#ffffff'),
}

def get_256_colors():
    for i in range(16, 256):
        ansi_colors[f'color_{i}'] = (f'\033[38;5;{i}m', f'#{i:02x}{i:02x}{i:02x}')
    return list(ansi_colors.keys())

def get_16_colors():
    return list(ansi_colors.keys())

# 설정 파일 로드
def load_settings(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 설정 파일 저장
def save_settings(settings, file_path):
    with open(file_path, 'w') as f:
        json.dump(settings, f, indent=4)

# 미리보기 라벨 업데이트
def update_color_preview(label, color_name):
    _, hex_color = ansi_colors[color_name]
    label.config(bg=hex_color, text=color_name)

# UI 생성 함수
def create_ui():
    settings = load_settings('colors.json')

    root = tk.Tk()
    root.title("Color Settings")

    for idx, section in enumerate(settings.keys()):
        label = tk.Label(root, text=section, width=20)
        label.grid(row=idx, column=0, padx=1, pady=5)
        
        combo = ttk.Combobox(root, values=get_16_colors(), width=20)
        combo.set(settings[section])
        combo.grid(row=idx, column=1, padx=5, pady=5)

        preview_label = tk.Label(root, text=settings[section], bg=ansi_colors[settings[section]][1], width=20, height=2)
        preview_label.grid(row=idx, column=2, padx=15, pady=5)

        def on_color_change(event, sec=section, combo=combo, pl=preview_label):
            color_name = combo.get()
            settings[sec] = color_name
            update_color_preview(pl, color_name)

        combo.bind("<<ComboboxSelected>>", on_color_change)

    def on_save():
        save_settings(settings, 'colors.json')
        root.destroy()

    save_button = tk.Button(root, text="Save", command=on_save, width=10, height=1)
    save_button.grid(row=len(settings), column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
