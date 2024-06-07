import json
import tkinter as tk
from tkinter import ttk
import os
import argparse

class Options:
    def __init__(self):
        self.verbose = False
        self.color_mode = '256'
        self.filepath = None
        self.backup_filepath = None
        
colors = {
    "verbose": '\033[38;5;118m',
}

# ANSI 색상 코드와 RGB 색상 매핑
ansi_colors = {
    "default": ('\033[0m', '#ffffff'),
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

def set_256_colors():
    for i in range(16, 232):
        r = ((i-16)//36)*51
        g = (((i-16)//6)%6)*51
        b = ((i-16)%6)*51
        ansi_colors[f'color_{i}'] = (f'\033[38;5;{i}m', f'#{r:02x}{g:02x}{b:02x}')
    for i in range(232, 256):
        gray = (i-232)*10 + 8
        ansi_colors[f'color_{i}'] = (f'\033[38;5;{i}m', f'#{gray:02x}{gray:02x}{gray:02x}')

def get_colors():
    return list(ansi_colors.keys())

# 설정 파일 로드
def load_settings(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 설정 파일 저장
def save_settings(settings, file_path):
    # 기존 파일 backup
    with open(file_path, 'r') as f:
        backup = f.read()
    
    # TODO: options.backup_filepath 와 일치하도록 수정
    with open(file_path + '.bak', 'w') as f:
        f.write(backup)
    
    with open(file_path, 'w') as f:
        json.dump(settings, f, indent=4)

# 미리보기 라벨 업데이트
def update_color_preview(label, color_name):
    _, hex_color = ansi_colors[color_name]
    label.config(bg=hex_color, text=color_name)

# UI 생성 함수
def create_ui(file_path):
    settings = load_settings(file_path)

    root = tk.Tk()
    root.title("Color Settings")

    for idx, section in enumerate(settings.keys()):
        label = tk.Label(root, text=section, width=20)
        label.grid(row=idx, column=0, padx=1, pady=5)
        
        combo = ttk.Combobox(root, values=get_colors(), width=20)
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
        save_settings(settings, file_path)
        root.destroy()

    save_button = tk.Button(root, text="Save", command=on_save, width=10, height=1)
    save_button.grid(row=len(settings), column=0, columnspan=3, pady=10)

    root.mainloop()

program_version = "0.1"

def get_parser():
    parser = argparse.ArgumentParser(description=f'set coloring config. ver: {program_version}')

    parser.add_argument('filepath', nargs='?', help='config file path, config file should be in json format, default is colors.json in the same directory as the this script')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    
    return parser
    
def set_options(args, options):
    options.verbose = args.verbose
    options.filepath = args.filepath
    
    if options.filepath is None:
        options.filepath = 'colors.json'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = 'colors.json'
        options.filepath = os.path.abspath(current_dir + '/' + filename)
        verbose('Open', f'using default config file: {options.filepath}', options)
    else:   
        # option에도 파일 경로 설정 : 백업 파일 경로 설정
        options.filepath = filepath
                
    options.backup_filepath = options.filepath + '.bak'
    verbose('Open', f'default config backup file path: {options.backup_filepath}', options)
    
def apply_color(text, color_name):
    ansi_code = colors.get(color_name, '\033[0m')
    return f"{ansi_code}{text}\033[0m"

def verbose(heading, message, options):
    if options.verbose:
        print(apply_color(f'{heading}: {message}', 'verbose'))

def get_terminal_colors():
    colors_supported = os.popen('tput colors').read()
    return int(colors_supported)

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    
    options = Options()
    set_options(args, options)
    
    filepath = options.filepath

    colors_supported = get_terminal_colors()
    verbose('Colors', f'{colors_supported} colors are supported.', options)
    if colors_supported < 256:
        options.color_mode = '16'
    else:
        options.color_mode = '256'
        set_256_colors()

    if not os.path.exists(filepath):
        verbose('Open', f'config file not found: {filepath}', options)
        exit(1)
    
    create_ui(filepath)
