import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os
import threading

class VideoConverterApp:
    """
    Главный класс нашего приложения для конвертации видео.
    Здесь мы создаём, настраиваем GUI и добавляем стили.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("🎥 Крутой видео конвертер")
        self.root.geometry("1024x860")  # Немного увеличим окно для красоты
        self.root.resizable(False, False)

        # Переменные для хранения путей и формата
        self.input_file_path = tk.StringVar()
        self.output_format = tk.StringVar(value="mp4")

        # --- Настройка стилей ---
        self.setup_styles()

        # --- Создание виджетов ---
        self.create_widgets()

    def setup_styles(self):
        """
        Здесь я настраиваю внешний вид приложения.
        Тёмная тема, новые шрифты и цвета для кнопок.
        """
        # Цветовая палитра
        BG_COLOR = "#2E2E2E"
        TEXT_COLOR = "#EAEAEA"
        BUTTON_BG = "#007ACC"
        BUTTON_FG = "#FFFFFF"
        BUTTON_ACTIVE_BG = "#005F9E"
        ENTRY_BG = "#3C3C3C"

        # Настраиваем стиль ttk
        style = ttk.Style(self.root)
        style.theme_use("clam") # Эта тема лучше всего поддаётся настройке

        # Общие стили для виджетов
        style.configure(".",
                        background=BG_COLOR,
                        foreground=TEXT_COLOR,
                        font=("Segoe UI", 10))

        style.configure("TFrame", background=BG_COLOR)

        # Стиль для кнопок
        style.configure("Accent.TButton",
                        font=("Segoe UI", 11, "bold"),
                        background=BUTTON_BG,
                        foreground=BUTTON_FG,
                        borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", BUTTON_ACTIVE_BG)],
                  foreground=[("active", BUTTON_FG)])

        # Стиль для выпадающего списка
        style.configure("TCombobox",
                        fieldbackground=ENTRY_BG,
                        background=BUTTON_BG,
                        arrowcolor=TEXT_COLOR,
                        foreground=TEXT_COLOR,
                        selectbackground=ENTRY_BG,
                        borderwidth=0)
        
        # Стиль для поля ввода
        style.configure("TEntry",
                        fieldbackground=ENTRY_BG,
                        foreground=TEXT_COLOR,
                        borderwidth=1,
                        relief="flat")
        
        # Стиль для метки статуса
        style.configure("Status.TLabel",
                        font=("Segoe UI", 9, "italic"),
                        foreground="#9A9A9A")


    def create_widgets(self):
        """
        Создаёт и размещает все элементы интерфейса в окне.
        """
        # --- Фрейм для контента ---
        # Отступы (padding) делают интерфейс "дышащим"
        content_frame = ttk.Frame(self.root, padding="20 20 20 20")
        content_frame.pack(expand=True, fill="both")

        # --- 1. Выбор файла ---
        input_label = ttk.Label(content_frame, text="1. Выберите ваш видеофайл:")
        input_label.pack(pady=(0, 5), anchor="w")

        # Создаём фрейм для поля ввода и кнопки, чтобы они были на одной линии
        file_frame = ttk.Frame(content_frame)
        file_frame.pack(fill="x", expand=True)

        input_entry = ttk.Entry(file_frame, textvariable=self.input_file_path, width=40, state="readonly")
        input_entry.pack(side="left", fill="x", expand=True, ipady=4)

        browse_button = ttk.Button(file_frame, text="🗂️ Обзор...", command=self.browse_file, style="Accent.TButton")
        browse_button.pack(side="left", padx=(10, 0))


        # --- 2. Выбор формата ---
        format_label = ttk.Label(content_frame, text="2. Выберите формат для конвертации:")
        format_label.pack(pady=(20, 5), anchor="w")

        formats = ["mp4", "avi", "mov", "wmv"]
        format_menu = ttk.Combobox(content_frame, textvariable=self.output_format, values=formats, state="readonly")
        format_menu.pack(fill="x", ipady=2)

        # --- 3. Кнопка конвертации ---
        # Используем наш новый "акцентный" стиль
        convert_button = ttk.Button(content_frame, text="🔄 Конвертировать", command=self.start_conversion_thread, style="Accent.TButton")
        convert_button.pack(pady=30, ipady=8, fill="x")

        # --- 4. Статус операции ---
        self.status_label = ttk.Label(content_frame, text="Готов к работе...", style="Status.TLabel", anchor="center")
        self.status_label.pack(pady=(10, 0), fill="x")

    def browse_file(self):
        """
        Открывает диалоговое окно для выбора видеофайла.
        """
        file_path = filedialog.askopenfilename(
            title="Выберите видеофайл",
            filetypes=(
                ("Видеофайлы", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("Все файлы", "*.*")
            )
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.status_label.config(text=f"Выбран файл: {os.path.basename(file_path)}")

    def start_conversion_thread(self):
        """
        Запускает процесс конвертации в отдельном потоке,
        чтобы не блокировать основной интерфейс.
        """
        # Проверяем, был ли выбран файл
        if not self.input_file_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, сначала выберите видеофайл.")
            return

        # Запускаем конвертацию в новом потоке
        conversion_thread = threading.Thread(target=self.convert_video, daemon=True)
        conversion_thread.start()

    def convert_video(self):
        """
        Выполняет конвертацию видео с помощью FFmpeg.
        """
        input_path = self.input_file_path.get()
        output_format = self.output_format.get()
        
        # Формируем имя выходного файла
        file_dir, file_name = os.path.split(input_path)
        file_base_name, _ = os.path.splitext(file_name)
        output_path = os.path.join(file_dir, f"{file_base_name}.{output_format}")

        # Обновляем статус в главном потоке
        self.root.after(0, self.status_label.config, {"text": "Конвертация... Пожалуйста, подождите."})

        try:
            # Команда для FFmpeg.
            # -i: входной файл
            # -y: перезаписать выходной файл, если он существует
            # -c:v copy -c:a copy: копировать кодеки без перекодирования (быстро)
            # Если нужно перекодирование, можно убрать -c:v и -c:a
            command = [
                "ffmpeg",
                "-i", input_path,
                "-y",
                output_path
            ]
            
            # Запускаем FFmpeg как подпроцесс
            # startupinfo нужен для Windows, чтобы не открывалось окно консоли
            si = None
            if os.name == 'nt':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(command, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Успешное завершение
                success_message = f"Готово! ✅\nФайл сохранён как:\n{output_path}"
                self.root.after(0, messagebox.showinfo, "Успех", success_message)
                self.root.after(0, self.status_label.config, {"text": "Конвертация успешно завершена."})
            else:
                # Если FFmpeg вернул ошибку
                error_message = f"Ошибка конвертации:\n{stderr}"
                self.root.after(0, messagebox.showerror, "Ошибка FFmpeg", error_message)
                self.root.after(0, self.status_label.config, {"text": "Произошла ошибка."})

        except FileNotFoundError:
            # Если FFmpeg не найден
            error_message = "FFmpeg не найден. Убедитесь, что он установлен и добавлен в PATH."
            self.root.after(0, messagebox.showerror, "Ошибка", error_message)
            self.root.after(0, self.status_label.config, {"text": "Ошибка: FFmpeg не найден."})
        except Exception as e:
            # Другие возможные ошибки
            error_message = f"Произошла непредвиденная ошибка:\n{e}"
            self.root.after(0, messagebox.showerror, "Критическая ошибка", error_message)
            self.root.after(0, self.status_label.config, {"text": "Произошла критическая ошибка."})

# --- Точка входа в приложение ---
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop() 