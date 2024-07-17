import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

settings_file = 'settings.json'
stringsets_dir = 'stringsets'
fonts_dir = 'fonts'

# Загрузка настроек из JSON файла при старте программы
try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    # Если файл не найден, используем пустой словарь
    settings = {}

# Создание окна
root = tk.Tk()
root.title("Настройки")
root.geometry("500x600")

# Цветовая палитра в формате RGB
COLOR_PALETTE = {
    "GRAY": (101, 101, 102),
    "WHITE": (230, 232, 235),
    "RED": (162, 47, 102),
    "PURPLE": (188, 152, 234),
    "BACKGROUND_COLOR": (36, 37, 38)
}

# Функция для сохранения настроек в JSON файл
def save_settings():
    for key, entry in entries.items():
        if key in COLOR_PALETTE:
            settings[key] = color_entries[key].get()
        else:
            value = entry.get()
            if key in ['MIN_LEN', 'MAX_LEN', 'FONTSIZE']:
                try:
                    settings[key] = int(value)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Значение для '{key}' должно быть целым числом.")
                    return
            else:
                settings[key] = value

    # Save combobox values explicitly
    for key in ['FILENAME', 'FONTNAME']:
        settings[key] = comboboxes[key].get()

    # Save boolean values explicitly
    for key in ['SHOW_LAYOUT', 'SHOW_UNDERLINE', 'SHOW_TAB']:
        settings[key] = bool_vars[key].get()

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)

# Получение списка файлов в директориях stringsets и fonts
file_list_stringsets = os.listdir(stringsets_dir)
file_list_fonts = os.listdir(fonts_dir)

# Создаем элементы интерфейса для каждой настройки
entries = {}
comboboxes = {}
bool_vars = {}
color_entries = {}

descriptions = {
    "MIN_LEN": "Минимальная длина итерации",
    "MAX_LEN": "Максимальная длина итерации",
    "SHOW_LAYOUT": "Показывать раскладку",
    "SHOW_UNDERLINE": "Показывать подчеркивание",
    "SHOW_TAB": "Показывать CAPS",
    "FONTNAME": "Шрифт",
    "FONTSIZE": "Размер шрифта",
    "FILENAME": "Файл данных",
    "GRAY": "Фантомные слова",
    "WHITE": "Напечатанные слова",
    "RED": "Ошибки в словах",
    "PURPLE": "Шкала прогресса",
    "BACKGROUND_COLOR": "Цвет фона",
}

# Создаем основной фрейм для всех элементов
main_frame = ttk.Frame(root)
main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

def choose_color(color_key, color_display):
    # Открываем диалоговое окно выбора цвета и получаем выбранный цвет
    color_code = colorchooser.askcolor(title="Выберите цвет")
    if color_code:
        # Сохраняем выбранный цвет в настройках
        settings['COLORS'][color_key] = color_code[0]
        save_settings()
        # Обновляем метку с текущим цветом
        color_display.config(text=str(color_code[0]))

# Функция для создания элементов интерфейса для цветов
def create_color_widgets(color_key):
    color_frame = ttk.Frame(main_frame)
    color_frame.pack(pady=5, padx=10, fill=tk.X)

    color_label = ttk.Label(color_frame, text=descriptions[color_key] + ":", width=30)
    color_label.pack(side=tk.LEFT)

    # Создаем метку для отображения текущего цвета
    color_display = ttk.Label(color_frame, text=str(settings['COLORS'][color_key]), width=20)
    color_display.pack(side=tk.LEFT)

    color_button = ttk.Button(color_frame, text="Выбрать цвет", command=lambda: choose_color(color_key, color_display))
    color_button.pack(side=tk.LEFT, padx=10)

# Создаем элементы интерфейса для каждой настройки
for key, value in settings.items():
    frame = ttk.Frame(main_frame)
    frame.pack(pady=5, padx=10, fill=tk.X)

    label_text = descriptions.get(key, key) + ":"
    label = ttk.Label(frame, text=label_text, width=30)
    label.pack(side=tk.LEFT)

    if key in ['FILENAME', 'FONTNAME']:
        combobox = ttk.Combobox(frame, state="readonly", width=20)
        if key == 'FILENAME':
            combobox['values'] = file_list_stringsets
        elif key == 'FONTNAME':
            combobox['values'] = file_list_fonts
        combobox.set(value)
        combobox.pack(side=tk.LEFT, padx=10)
        combobox.bind("<<ComboboxSelected>>", lambda event, key=key: save_settings())
        comboboxes[key] = combobox
    elif key in ['SHOW_LAYOUT', 'SHOW_UNDERLINE', 'SHOW_TAB']:
        bool_var = tk.BooleanVar(value=bool(value))
        checkbox = ttk.Checkbutton(frame, variable=bool_var, command=save_settings)
        checkbox.pack(side=tk.LEFT, padx=10)
        bool_vars[key] = bool_var
    elif key == 'COLORS':
        for color_key in COLOR_PALETTE:
            create_color_widgets(color_key)
    else:
        entry = ttk.Entry(frame, font=("Arial", 12), width=20)
        entry.insert(0, str(value))
        entry.pack(side=tk.LEFT, padx=10)

        def make_update_func(key):
            def update(event):
                save_settings()
            return update

        entry.bind("<FocusOut>", make_update_func(key))
        entries[key] = entry

# Кнопка для сохранения настроек
save_button = ttk.Button(root, text="Сохранить", command=save_settings)
save_button.pack(pady=10)

root.mainloop()
