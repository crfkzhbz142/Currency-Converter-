import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор паролей")
        self.root.geometry("400x250")

        # Переменная для длины пароля
        self.length = tk.IntVar(value=12)
        # Переменные для выбора состава пароля
        self.use_letters = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=False)
        self.use_symbols = tk.BooleanVar(value=False)

        self.setup_ui()

    def setup_ui(self):
        # Поле для выбора длины
        ttk.Label(self.root, text="Длина пароля:").pack(pady=5)
        length_scale = ttk.Scale(
            self.root,
            from_=4,
            to=64,
            orient="horizontal",
            variable=self.length
        )
        length_scale.pack(fill="x", padx=20)
        self.length_label = ttk.Label(self.root, text=f"{self.length.get()} символов")
        self.length_label.pack()

        # Обновление метки при движении ползунка
        length_scale.config(command=self.update_length_label)

        # Флажки для выбора состава
        ttk.Checkbutton(
            self.root,
            text="Буквы (a-z, A-Z)",
            variable=self.use_letters
        ).pack(anchor="w", padx=20)
        ttk.Checkbutton(
            self.root,
            text="Цифры (0-9)",
            variable=self.use_digits
        ).pack(anchor="w", padx=20)
        ttk.Checkbutton(
            self.root,
            text="Специальные символы (!@#$% и т.д.)",
            variable=self.use_symbols
        ).pack(anchor="w", padx=20)

        # Кнопка генерации
        generate_btn = ttk.Button(
            self.root,
            text="Сгенерировать",
            command=self.generate_password
        )
        generate_btn.pack(pady=10)

        # Поле вывода пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            self.root,
            textvariable=self.password_var,
            state="readonly",
            font=("Courier", 10)
        )
        password_entry.pack(fill="x", padx=20, pady=5)

        # Кнопка копирования
        copy_btn = ttk.Button(
            self.root,
            text="Копировать в буфер обмена",
            command=self.copy_to_clipboard
        )
        copy_btn.pack(pady=5)

    def update_length_label(self, value):
        self.length_label.config(text=f"{int(float(value))} символов")

    def generate_password(self):
        # Формирование набора символов
        chars = ""
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_digits.get():
            chars += string.digits
        if self.use_symbols.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов!")
            return

        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(self.length.get()))
        self.password_var.set(password)

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

