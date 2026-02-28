"""
coverage report -m
"""

"""
Главный модуль программы с интерактивным меню
Реализация настоящих двоичных операций
"""

import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.binary_processor import BinaryProcessor
from src.integer_operations import IntegerCodeConverter, IntegerArithmetic
from src.float_operations import IEEE754Converter, FloatArithmetic
from src.bcd_operations import BCD8421Converter, BCDArithmetic
from src.utils import BinaryArrayUtils, NumberConverter


class InteractiveMenu:
    """
    Интерактивное меню для работы с программой
    """

    def __init__(self):
        """Инициализация меню"""
        self.processor = BinaryProcessor()
        self.utils = BinaryArrayUtils()
        self.converter = NumberConverter()

        # Инициализация конвертеров и арифметики
        self.int_converter = IntegerCodeConverter(self.processor)
        self.int_arithmetic = IntegerArithmetic(self.processor, self.int_converter)
        self.ieee_converter = IEEE754Converter(self.processor)
        self.float_arithmetic = FloatArithmetic(self.processor, self.ieee_converter)
        self.bcd_converter = BCD8421Converter(self.processor)
        self.bcd_arithmetic = BCDArithmetic(self.processor, self.bcd_converter)

        # Флаг для продолжения работы
        self.running = True

    def print_header(self, text):
        """Вывод заголовка"""
        print("\n" + "=" * 70)
        print(f" {text}")
        print("=" * 70)

    def print_menu(self):
        """Вывод главного меню"""


        print(" Вариант: 8421 BCD")

        print("\nГЛАВНОЕ МЕНЮ:")
        print("-" * 40)
        print("1. Представление чисел в разных кодах")
        print("2. Сложение чисел в дополнительном коде")
        print("3. Вычитание чисел (через сложение)")
        print("4. Умножение чисел в прямом коде (ДВОИЧНОЕ)")
        print("5. Деление чисел в прямом коде (ДВОИЧНОЕ)")
        print("6. Операции с плавающей точкой (IEEE 754)")
        print("7. Операции с BCD 8421 кодом")
        print("8. Показать все операции на примерах")
        print("0. Выход")
        print("-" * 40)

    def get_integer(self, prompt):
        """Получение целого числа от пользователя"""
        while True:
            try:
                value = int(input(prompt))
                return value
            except ValueError:
                print(" Ошибка: введите целое число!")

    def get_float(self, prompt):
        """Получение числа с плавающей точкой от пользователя"""
        while True:
            try:
                value = float(input(prompt))
                return value
            except ValueError:
                print(" Ошибка: введите число!")

    def get_positive_integer(self, prompt):
        """Получение положительного целого числа"""
        while True:
            try:
                value = int(input(prompt))
                if value >= 0:
                    return value
                print(" Ошибка: введите неотрицательное число!")
            except ValueError:
                print(" Ошибка: введите целое число!")

    def wait_for_enter(self):
        """Ожидание нажатия Enter"""
        input("\nНажмите Enter для продолжения...")

    # ==================== ОПЕРАЦИИ ====================

    def operation_codes(self):
        """Операция 1: Представление чисел в разных кодах"""
        self.print_header("ПРЕДСТАВЛЕНИЕ ЧИСЕЛ В РАЗНЫХ КОДАХ")

        number = self.get_integer("\nВведите целое число: ")

        print(f"\nЧисло: {number}")
        print("-" * 50)

        # Прямой код
        direct = self.int_converter.get_direct_code(number)
        print(f"Прямой код:     {self.utils.format_binary(direct)}")

        # Обратный код
        reverse = self.int_converter.get_reverse_code(number)
        print(f"Обратный код:   {self.utils.format_binary(reverse)}")

        # Дополнительный код
        additional = self.int_converter.get_additional_code(number)
        print(f"Дополнительный: {self.utils.format_binary(additional)}")

        # Проверка обратного преобразования
        recovered = self.int_converter.additional_to_decimal(additional)
        print(f"\nПроверка (доп. код -> десятичное): {recovered}")

        self.wait_for_enter()

    def operation_addition(self):
        """Операция 2: Сложение в дополнительном коде"""
        self.print_header("СЛОЖЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ")

        print("\nВведите два числа:")
        a = self.get_integer("Первое число: ")
        b = self.get_integer("Второе число: ")

        result = self.int_arithmetic.add_in_additional_code(a, b)

        print(f"\n{a} + {b} = {result['result_decimal']}")
        print("-" * 50)
        print(f"Первое число в доп. коде:  {self.utils.format_binary(result['first_binary'])}")
        print(f"Второе число в доп. коде:  {self.utils.format_binary(result['second_binary'])}")
        print(f"Результат в доп. коде:     {self.utils.format_binary(result['result_binary'])}")

        self.wait_for_enter()

    def operation_subtraction(self):
        """Операция 3: Вычитание через сложение"""
        self.print_header("ВЫЧИТАНИЕ ЧЕРЕЗ СЛОЖЕНИЕ")

        print("\nВведите два числа:")
        a = self.get_integer("Уменьшаемое: ")
        b = self.get_integer("Вычитаемое: ")

        result = self.int_arithmetic.subtract_in_additional_code(a, b)

        print(f"\n{a} - {b} = {result['result_decimal']}")
        print("-" * 50)
        print(f"Результат в доп. коде: {self.utils.format_binary(result['result_binary'])}")

        self.wait_for_enter()

    def operation_multiplication(self):
        """Операция 4: Умножение в прямом коде (НАСТОЯЩЕЕ ДВОИЧНОЕ)"""
        self.print_header("УМНОЖЕНИЕ В ПРЯМОМ КОДЕ (ДВОИЧНОЕ)")

        print("\nВведите два числа:")
        a = self.get_integer("Первый множитель: ")
        b = self.get_integer("Второй множитель: ")

        result = self.int_arithmetic.multiply_in_direct_code(a, b)

        self.wait_for_enter()

    def operation_division(self):
        """Операция 5: Деление в прямом коде (НАСТОЯЩЕЕ ДВОИЧНОЕ)"""
        self.print_header("ДЕЛЕНИЕ В ПРЯМОМ КОДЕ (ДВОИЧНОЕ)")

        print("\nВведите два числа:")
        a = self.get_integer("Делимое: ")
        b = self.get_integer("Делитель: ")

        if b == 0:
            print("\n Ошибка: деление на ноль невозможно!")
            self.wait_for_enter()
            return

        precision = self.get_integer("Введите точность (знаков после запятой): ")

        result = self.int_arithmetic.divide_in_direct_code(a, b, precision)

        self.wait_for_enter()

    def operation_float(self):
        """Операция 6: Операции с плавающей точкой"""
        self.print_header("ОПЕРАЦИИ С ПЛАВАЮЩЕЙ ТОЧКОЙ (IEEE 754)")

        print("\nВыберите операцию:")
        print("1. Сложение")
        print("2. Вычитание")
        print("3. Умножение")
        print("4. Деление")

        choice = input("\nВаш выбор (1-4): ").strip()

        if choice not in ['1', '2', '3', '4']:
            print(" Неверный выбор!")
            self.wait_for_enter()
            return

        print("\nВведите два числа:")
        a = self.get_float("Первое число: ")
        b = self.get_float("Второе число: ")

        if choice == '4' and b == 0:
            print("\n Ошибка: деление на ноль невозможно!")
            self.wait_for_enter()
            return

        operations = {
            '1': ('сложения', self.float_arithmetic.add),
            '2': ('вычитания', self.float_arithmetic.subtract),
            '3': ('умножения', self.float_arithmetic.multiply),
            '4': ('деления', self.float_arithmetic.divide)
        }

        op_name, op_func = operations[choice]
        result = op_func(a, b)

        print(f"\nРезультат {op_name}: {result['result_decimal']}")
        print("-" * 50)
        print(f"Первое число в IEEE 754:  {self.utils.format_binary(result['first_binary'])}")
        print(f"Второе число в IEEE 754:  {self.utils.format_binary(result['second_binary'])}")
        print(f"Результат в IEEE 754:     {self.utils.format_binary(result['result_binary'])}")

        self.wait_for_enter()

    def operation_bcd(self):
        """Операция 7: Операции с BCD кодом"""
        self.print_header("ОПЕРАЦИИ С BCD 8421 КОДОМ")

        print("\nВведите два положительных числа:")
        a = self.get_positive_integer("Первое число: ")
        b = self.get_positive_integer("Второе число: ")

        try:
            result = self.bcd_arithmetic.add(a, b)

            print(f"\n{a} + {b} = {result['result_decimal']}")
            print("-" * 50)
            print(f"Первое число в BCD:  {self.utils.format_binary(result['first_binary'], 4)}")
            print(f"Второе число в BCD:  {self.utils.format_binary(result['second_binary'], 4)}")
            print(f"Результат в BCD:     {self.utils.format_binary(result['result_binary'], 4)}")

            # Проверка обратного преобразования
            recovered = self.bcd_converter.bcd_to_decimal(result['first_binary'])
            print(f"\nПроверка BCD -> десятичное: {a} -> {recovered}")

        except ValueError as e:
            print(f"\n Ошибка: {e}")

        self.wait_for_enter()

    def operation_demo(self):
        """Операция 8: Демонстрация всех операций"""
        self.print_header("ДЕМОНСТРАЦИЯ ВСЕХ ОПЕРАЦИЙ")

        print("\nЗапуск демонстрации с предустановленными значениями...\n")

        # Целые числа
        print("1. ПРЕДСТАВЛЕНИЕ ЧИСЕЛ В КОДАХ")
        print("-" * 40)
        for num in [42, -42]:
            codes = self.int_converter.get_all_codes(num)
            print(f"\nЧисло: {num}")
            print(f"  Прямой:     {self.utils.format_binary(codes['direct'])}")
            print(f"  Обратный:   {self.utils.format_binary(codes['reverse'])}")
            print(f"  Дополнит:   {self.utils.format_binary(codes['additional'])}")

        # Умножение
        print("\n2. УМНОЖЕНИЕ (ДВОИЧНОЕ)")
        print("-" * 40)
        self.int_arithmetic.multiply_in_direct_code(7, 6)

        # Деление
        print("\n3. ДЕЛЕНИЕ (ДВОИЧНОЕ)")
        print("-" * 40)
        self.int_arithmetic.divide_in_direct_code(100, 7, 5)

        # Плавающая точка
        print("\n4. ПЛАВАЮЩАЯ ТОЧКА (IEEE 754)")
        print("-" * 40)
        a, b = 12.375, 5.25
        result = self.float_arithmetic.add(a, b)
        print(f"{a} + {b} = {result['result_decimal']}")
        print(f"  IEEE 754: {self.utils.format_binary(result['result_binary'])}")

        # BCD
        print("\n5. BCD 8421")
        print("-" * 40)
        a, b = 123, 456
        result = self.bcd_arithmetic.add(a, b)
        print(f"{a} + {b} = {result['result_decimal']}")
        print(f"  BCD: {self.utils.format_binary(result['result_binary'], 4)}")

        self.wait_for_enter()

    def run(self):
        """Запуск меню"""
        while self.running:
            self.print_menu()

            choice = input("\nВыберите действие (0-8): ").strip()

            if choice == '1':
                self.operation_codes()
            elif choice == '2':
                self.operation_addition()
            elif choice == '3':
                self.operation_subtraction()
            elif choice == '4':
                self.operation_multiplication()
            elif choice == '5':
                self.operation_division()
            elif choice == '6':
                self.operation_float()
            elif choice == '7':
                self.operation_bcd()
            elif choice == '8':
                self.operation_demo()
            elif choice == '0':
                self.running = False
                print("\nДо свидания!")
            else:
                print("\n Неверный выбор! Нажмите Enter и попробуйте снова.")
                self.wait_for_enter()


def main():
    """Главная функция"""
    menu = InteractiveMenu()

    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\n Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()

    print("\nРабота завершена.")


if __name__ == "__main__":
    main()