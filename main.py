import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("600x500")

        # API ключ (замените на ваш)
        self.api_key = "YOUR_API_KEY"  # Получите на exchangerate-api.com
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/"


        # Файл для хранения истории
        self.history_file = "history.json"


        # Загрузка истории из JSON
        self.history = self.load_history_from_json()

        self.setup_ui()
        self.load_currencies()

    def setup_ui(self):
        """Создание интерфейса"""
        # Заголовок
        ttk.Label(self.root, text="Конвертер валют", font=("Arial", 16)).pack(pady=10)

        # Выбор валют
        frame_currencies = ttk.Frame(self.root)
        frame_currencies.pack(pady=5)

        ttk.Label(frame_currencies, text="Из:").grid(row=0, column=0)
        self.from_currency = ttk.Combobox(frame_currencies, width=10)
        self.from_currency.grid(row=0, column=1, padx=5)

        ttk.Label(frame_currencies, text="В:").grid(row=0, column=2)
        self.to_currency = ttk.Combobox(frame_currencies, width=10)
        self.to_currency.grid(row=0, column=3, padx=5)

        # Поле ввода суммы
        frame_amount = ttk.Frame(self.root)
        frame_amount.pack(pady=5)
        ttk.Label(frame_amount, text="Сумма:").pack(side="left")
        self.amount_entry = ttk.Entry(frame_amount, width=20)
        self.amount_entry.pack(side="left", padx=5)

        # Кнопка конвертации
        convert_btn = ttk.Button(
            self.root,
            text="Конвертировать",
            command=self.convert_currency
        )
        convert_btn.pack(pady=10)

        # Результат
        self.result_label = ttk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)

        # История конвертаций
        ttk.Label(self.root, text="История конвертаций:").pack()
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)

        # Настройка колонок
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        self.history_tree.pack(fill="both", expand=True, padx=20, pady=5)


        # Обновление отображения истории
        self.update_history_display()

    def load_currencies(self):
        """Загрузка списка валют с API"""
        try:
            response = requests.get(f"{self.base_url}USD")
            # Проверка HTTP-статуса
            if response.status_code != 200:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                return

            data = response.json()
            currencies = sorted(data['conversion_rates'].keys())
            self.from_currency['values'] = currencies
            self.to_currency['values'] = currencies

            # Установка значений по умолчанию
            if 'USD' in currencies:
                self.from_currency.set("USD")
            else:
                self.from_currency.set(currencies[0])

            if 'EUR' in currencies:
                self.to_currency.set("EUR")
            else:
                self.to_currency.set(currencies[1] if len(currencies) > 1 else currencies[0])
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Проблема с подключением к API: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить валюты: {e}")

    def convert_currency(self):
        """Конвертация валюты и сохранение в историю"""
        try:
            # Проверка и преобразование суммы
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                messagebox.showerror("Ошибка", "Введите сумму для конвертации!")
                return

            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return

            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if not from_curr or not to_curr:
                messagebox.showerror("Ошибка", "Выберите валюты для конвертации!")
                return

            # Получение курса через API
            response = requests.get(f"{self.base_url}{from_curr}")
            # Проверка HTTP-статуса
            if response.status_code != 200:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                return

            data = response.json()

            if to_curr in data['conversion_rates']:
                rate = data['conversion_rates'][to_curr]
                result = amount * rate

                # Отображение результата
                self.result_label.config(
                    text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
                )


                # Создание записи для истории
                history_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": round(amount, 2),
                    "from": from_curr,
                    "to": to_curr,
            "rate": round(rate, 6),
            "result": round(result, 2)
                }

                # Добавление в историю и сохранение в JSON
                self.history.append(history_entry)
                self.save_history_to_json()  # Вызов без аргументов
                self.update_history_display()
            else:
                messagebox.showerror("Ошибка", "Неизвестный код валюты!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число в поле суммы!")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Нет подключения к интернету или проблема с API!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def load_history_from_json(self):
        """Загрузка истории из JSON-файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить историю: {e}. Создаётся новая история.")
                return []
        else:
            # Создаём пустой файл истории, если его нет
            self.save_history_to_json()  # Вызов без аргументов
            return []

    def save_history_to_json(self):
        """Сохранение истории в JSON-файл"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def update_history_display(self):
        """Обновление отображения истории в таблице"""
        # Очистка текущей таблицы
        for item in self.history
