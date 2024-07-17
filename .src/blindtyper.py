import pygame
import random
import time
import ctypes
import json
import os
import subprocess

# Инициализация Pygame
pygame.init()

# Установки экрана
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Typing Trainer")

# Загрузка настроек из JSON файла
with open('settings.json', 'r') as f:
    settings = json.load(f)

## Использование настроек из JSON файла
MIN_LEN = settings["MIN_LEN"]
MAX_LEN = settings["MAX_LEN"]
FILENAME = settings["FILENAME"]
SHOW_LAYOUT = settings["SHOW_LAYOUT"]
SHOW_UNDERLINE = settings["SHOW_UNDERLINE"]
SHOW_TAB = settings["SHOW_TAB"]
FONTNAME = settings["FONTNAME"]
FONTSIZE = settings["FONTSIZE"]
COLORS = settings["COLORS"]

# Распаковка цветов из словаря
GRAY = COLORS["GRAY"]
WHITE = COLORS["WHITE"]
RED = COLORS["RED"]
PURPLE = COLORS["PURPLE"]
BACKGROUND_COLOR = COLORS["BACKGROUND_COLOR"]

# Установки экрана
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Typing Trainer")

# paths
FONT = pygame.font.Font(f"fonts/{FONTNAME}", FONTSIZE)
FILE = f"stringsets/{FILENAME}"

def display_text(surface, text, position, color):
    text_surface = FONT.render(text, True, color)
    surface.blit(text_surface, position)


def generate_string(words, min_length=MIN_LEN, max_length=MAX_LEN):
    length = random.randint(min_length, max_length)
    return ' '.join(random.choice(words) for _ in range(length)).rstrip()


def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # Проверяем каждую часть слова (в случае, если слово длиннее максимальной ширины)
        for part in break_word_into_parts(word, font, max_width):
            # Проверяем, поместится ли слово на текущей строке
            if font.size(' '.join(current_line + [part]))[0] <= max_width:
                current_line.append(part)
            else:
                # Если слово не поместится, начинаем новую строку
                lines.append(' '.join(current_line))
                current_line = [part]

    lines.append(' '.join(current_line))
    return lines


def break_word_into_parts(word, font, max_width):
    parts = []
    current_part = ""

    for char in word:
        if font.size(current_part + char)[0] <= max_width:
            current_part += char
        else:
            parts.append(current_part)
            current_part = char

    parts.append(current_part)
    return parts


def load_strings_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]


def get_keyboard_layout():
    if os.name == 'nt':
        import ctypes
        user32 = ctypes.WinDLL('user32')
        layout = user32.GetKeyboardLayout(0)
        language_id = layout & (2 ** 16 - 1)
        if language_id == 0x419:
            return "ru"
        else:
            return "en"
    elif os.name == 'posix':
        return "??"


print(get_keyboard_layout())


def main():
    running = True
    # Загрузка строк из файла
    strings = load_strings_from_file(FILE)

    while running:
        # Генерация случайной строки из загруженного набора строк
        current_string = generate_string(strings)
        typed_string = ""
        start_time = time.time()

        while True:
            screen.fill(BACKGROUND_COLOR)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        break
                    elif event.key == pygame.K_BACKSPACE:
                        typed_string = typed_string[:-1]
                    elif event.unicode.isprintable() and len(typed_string) < len(current_string):
                        typed_string += event.unicode

            # Отображение строки
            lines = wrap_text(current_string, FONT, SCREEN_WIDTH - 100)
            y_offset = 100
            total_chars = 0
            for line in lines:
                x_offset = 50
                for char in line:
                    if total_chars < len(typed_string):
                        if typed_string[total_chars] == char:
                            text_color = WHITE
                        else:
                            text_color = RED
                    else:
                        text_color = GRAY

                    display_text(screen, char, (x_offset, y_offset), text_color)

                    # Добавление подчеркивания под текущей буквой
                    if SHOW_UNDERLINE and total_chars == len(typed_string):
                        char_width, char_height = FONT.size(char)
                        pygame.draw.line(screen, WHITE, (x_offset, y_offset + char_height), (x_offset + char_width, y_offset + char_height), 2)

                    x_offset += FONT.size(char)[0]
                    total_chars += 1

                y_offset += FONT.get_height()

            # Полоска прогресса
            progress = len(typed_string) / (len(current_string)-len(lines)+1)
            pygame.draw.rect(screen, GRAY, (50, 50, SCREEN_WIDTH - 100, 20))
            pygame.draw.rect(screen, PURPLE, (50, 50, (SCREEN_WIDTH - 100) * progress, 20))

            # Отображение статуса CAPS LOCK
            caps_lock_status = "CAPSLOCK" if pygame.key.get_mods() & pygame.KMOD_CAPS else ""
            if SHOW_TAB:
                display_text(screen, caps_lock_status, (SCREEN_WIDTH - 330, SCREEN_HEIGHT - 100),
                             RED if caps_lock_status else WHITE)

            # Отображение текущей раскладки
            current_layout = get_keyboard_layout()
            if SHOW_LAYOUT:
                display_text(screen, current_layout, (50, SCREEN_HEIGHT - 100), WHITE)

            # Подсчет WPM и CPM
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > 0:
                wpm = (len(typed_string.split()) / elapsed_time) * 60
                cpm = (len(typed_string) / elapsed_time) * 60
            else:
                wpm = 0
                cpm = 0

            # Отображение результатов WPM и CPM
            display_text(screen, f"WPM: {wpm:.1f}", (50, y_offset + 50), WHITE)
            display_text(screen, f"CPM: {cpm:.1f}", (500, y_offset + 50), WHITE)

            pygame.display.flip()

            # Если введена полная строка, завершаем цикл и выбираем новую строку
            if len(typed_string) >= (len(current_string)-len(lines)+1):
                break

        # Задержка перед началом следующего цикла
        time.sleep(1)

    pygame.quit()


if __name__ == "__main__":
    main()
