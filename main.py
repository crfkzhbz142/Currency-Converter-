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
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"

        # Загрузка истории
        self.history = self.load_history()

        self.setup_ui()
        self.load_currencies()

    def setup_ui(self):
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

        # История
        ttk.Label(self.root, text="История конвертаций:").pack()
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        self.history_tree.pack(fill="both", expand=True, padx=20, pady=5)

        # Обновление истории
        self.update_history_display()

    def load_currencies(self):
        """Загрузка списка валют"""
        try:
            response = requests.get(f"{self.base_url}USD")
            data = response.json()
            currencies = sorted(data['rates'].keys())
            self.from_currency['values'] = currencies
            self.to_currency['values'] = currencies
            # Установка значений по умолчанию
            self.from_currency.set("USD")
            self.to_currency.set("EUR")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить валюты: {e}")

    def convert_currency(self):
        """Конвертация валюты"""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return

            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if not from_curr or not to_curr:
                messagebox.showerror("Ошибка", "Выберите валюты!")
                return

            # Получение курса
            response = requests.get(f"{self.base_url}{from_curr}")
            data = response.json()

            if to_curr in data['rates']:
                rate = data['rates'][to_curr]
                result = amount * rate

                # Отображение результата
                self.result_label.config(
                    text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
                )

                # Добавление в историю
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_entry = {
                    "date": timestamp,
                    "amount": amount,
                    "from": from_curr,
                    "to": to_curr,
                    "result": result
                }
                self.history.append(history_entry)
                self.save_history()
                self.update_history_display()
            else:
                messagebox.showerror("Ошибка", "Неизвестный код валюты!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка конвертации: {e}")

    def load_history(self):
        """Загрузка истории из файла"""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """Сохранение истории в файл"""
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def update_history_display(self):
        """Обновление отображения истории"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for entry in reversed(self.history[-10:]):  # Последние 10 записей
            self.history_tree.insert(
                "", "end",
                values=(
                    entry["date"],
                    f"{entry['amount']:.2f}",
                    entry["from"],
                    entry["to"],
                    f"{entry['result']:.2f}"
                )
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
