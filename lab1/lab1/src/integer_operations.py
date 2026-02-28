"""
Операции с целыми числами в различных кодах
"""

"""
Операции с целыми числами в различных кодах
Реализация настоящих двоичных операций
"""

from src.binary_processor import BinaryProcessor
from src.utils import NumberConverter


class IntegerCodeConverter:
    """
    Конвертер для различных кодов представления целых чисел
    """

    def __init__(self, processor):
        """
        Инициализация конвертера

        Args:
            processor: экземпляр BinaryProcessor
        """
        self.processor = processor
        self.converter = NumberConverter()

    def get_direct_code(self, decimal_number):
        """
        Получение прямого кода числа

        Args:
            decimal_number: десятичное число

        Returns:
            массив прямого кода (32 бита)
        """
        is_negative = decimal_number < 0
        binary_digits = self.converter.integer_to_binary_array(decimal_number)

        result = self.processor.create_zero_array()
        digits_length = len(binary_digits)

        # Копируем двоичное представление (выравнивание по правому краю)
        start_position = self.processor.INTEGER_BITS - digits_length + 1
        for index in range(digits_length):
            result[start_position + index] = binary_digits[index]

        # Устанавливаем знаковый бит
        if is_negative:
            result[self.processor.SIGN_BIT_INDEX] = 1

        return result

    def get_reverse_code(self, decimal_number):
        """
        Получение обратного кода числа

        Args:
            decimal_number: десятичное число

        Returns:
            массив обратного кода (32 бита)
        """
        direct_code = self.get_direct_code(decimal_number)

        if decimal_number >= 0:
            return direct_code
        else:
            return self.processor.invert_bits(direct_code)

    def get_additional_code(self, decimal_number):
        """
        Получение дополнительного кода числа

        Args:
            decimal_number: десятичное число

        Returns:
            массив дополнительного кода (32 бита)
        """
        if decimal_number >= 0:
            return self.get_direct_code(decimal_number)

        reverse_code = self.get_reverse_code(decimal_number)
        additional_code = self.processor.add_binary_arrays(
            reverse_code,
            self.processor.get_binary_one()
        )

        return additional_code

    def additional_to_decimal(self, additional_array):
        """
        Преобразование дополнительного кода в десятичное число

        Args:
            additional_array: массив дополнительного кода

        Returns:
            десятичное число
        """
        self.processor.utils.validate_binary_array(additional_array)

        # Проверяем знаковый бит
        if additional_array[self.processor.SIGN_BIT_INDEX] == 0:
            # Положительное число
            value = 0
            for i in range(1, self.processor.BIT_COUNT):
                value = value * 2 + additional_array[i]
            return value

        # Отрицательное число: инвертируем, вычитаем 1 и меняем знак
        inverted = self.processor.invert_bits(additional_array)

        # Вычитаем 1 (сложение с дополнительным кодом -1)
        minus_one = self.processor.create_zero_array()
        minus_one[self.processor.BIT_COUNT - 1] = 1

        # Вычитание через сложение с дополнительным кодом
        # Для вычитания 1 нужно прибавить число, у которого все биты 1 (это -1 в доп. коде)
        all_ones = [1] * self.processor.BIT_COUNT
        subtracted = self.processor.add_binary_arrays(inverted, all_ones)

        # Получаем абсолютное значение
        absolute_value = 0
        for i in range(1, self.processor.BIT_COUNT):
            absolute_value = absolute_value * 2 + subtracted[i]

        return -absolute_value

    def get_all_codes(self, decimal_number):
        """
        Получение всех кодов числа

        Args:
            decimal_number: десятичное число

        Returns:
            словарь с кодами
        """
        return {
            'decimal': decimal_number,
            'direct': self.get_direct_code(decimal_number),
            'reverse': self.get_reverse_code(decimal_number),
            'additional': self.get_additional_code(decimal_number)
        }


class IntegerArithmetic:
    """
    Арифметические операции с целыми числами
    Реализация настоящих двоичных операций
    """

    def __init__(self, processor, code_converter):
        """
        Инициализация арифметики

        Args:
            processor: экземпляр BinaryProcessor
            code_converter: экземпляр IntegerCodeConverter
        """
        self.processor = processor
        self.converter = NumberConverter()
        self.code_converter = code_converter or IntegerCodeConverter(processor)

    def add_in_additional_code(self, first_number, second_number):
        """
        Сложение чисел в дополнительном коде

        Args:
            first_number: первое слагаемое
            second_number: второе слагаемое

        Returns:
            словарь с результатами
        """
        first_additional = self.code_converter.get_additional_code(first_number)
        second_additional = self.code_converter.get_additional_code(second_number)

        sum_additional = self.processor.add_binary_arrays(
            first_additional,
            second_additional
        )
        sum_decimal = self.code_converter.additional_to_decimal(sum_additional)

        return {
            'first': first_number,
            'second': second_number,
            'result_decimal': sum_decimal,
            'result_binary': sum_additional,
            'first_binary': first_additional,
            'second_binary': second_additional
        }

    def subtract_in_additional_code(self, minuend, subtrahend):
        """
        Вычитание через сложение с отрицательным вычитаемым

        Args:
            minuend: уменьшаемое
            subtrahend: вычитаемое

        Returns:
            словарь с результатами
        """
        return self.add_in_additional_code(minuend, -subtrahend)

    # ========== НАСТОЯЩЕЕ ДВОИЧНОЕ УМНОЖЕНИЕ ==========

    def multiply_in_direct_code(self, first_number, second_number):
        """
        Умножение чисел в прямом коде (НАСТОЯЩЕЕ ДВОИЧНОЕ УМНОЖЕНИЕ)
        Используется алгоритм умножения столбиком в двоичной системе
        """
        # Определяем знак результата
        first_sign = 1 if first_number < 0 else 0
        second_sign = 1 if second_number < 0 else 0
        result_sign = first_sign ^ second_sign  # XOR

        # Берем модули чисел (без знакового бита)
        first_abs = abs(first_number)
        second_abs = abs(second_number)

        # Получаем двоичные представления модулей
        first_binary = self.converter.integer_to_binary_array(first_abs)
        second_binary = self.converter.integer_to_binary_array(second_abs)

        print(f"\n Двоичное представление множителей:")
        print(f"  {first_number} = {first_binary}")
        print(f"  {second_number} = {second_binary}")

        # ДВОИЧНОЕ УМНОЖЕНИЕ СТОЛБИКОМ
        print(f"\n Процесс умножения в двоичной системе:")
        print(f"{'=' * 60}")

        # Создаем массив для результата (максимальная длина = сумма длин)
        max_length = len(first_binary) + len(second_binary)
        result_binary = [0] * max_length

        # Пошаговое умножение
        intermediate_results = []

        for i, bit in enumerate(reversed(second_binary)):
            if bit == 1:
                # Сдвигаем первое число на i позиций влево
                shifted = first_binary.copy() + [0] * i

                # Выравниваем длину для сложения
                while len(shifted) < max_length:
                    shifted.insert(0, 0)

                print(f"  Шаг {i + 1}: {bit} × {first_binary} = {shifted}")
                intermediate_results.append(shifted)

        # Складываем все промежуточные результаты
        print(f"\n Сложение промежуточных результатов:")
        for idx, res in enumerate(intermediate_results):
            print(f"  Промежуточный {idx + 1}: {res}")
            result_binary = self._binary_add(result_binary, res)

        # Убираем ведущие нули
        while len(result_binary) > 1 and result_binary[0] == 0:
            result_binary.pop(0)

        # Переводим результат в десятичное для проверки
        result_abs = self._binary_to_decimal(result_binary)

        # Применяем знак
        if result_sign == 1:
            result_abs = -result_abs

        # Получаем прямой код для 32-битного представления
        result_direct = self.code_converter.get_direct_code(result_abs)

        print(f"\n Результат умножения:")
        print(f"  Двоичный результат: {result_binary}")
        print(f"  Десятичный результат: {result_abs}")
        print(f"  32-битный прямой код: {self.processor.utils.format_binary(result_direct)}")

        return {
            'first': first_number,
            'second': second_number,
            'result_decimal': result_abs,
            'result_binary': result_direct,
            'binary_result': result_binary
        }

    def _binary_add(self, a, b):
        """
        Вспомогательный метод для сложения двоичных чисел (без знака)
        """
        max_len = max(len(a), len(b))
        a_padded = [0] * (max_len - len(a)) + a
        b_padded = [0] * (max_len - len(b)) + b

        result = [0] * (max_len + 1)
        carry = 0

        for i in range(max_len - 1, -1, -1):
            total = a_padded[i] + b_padded[i] + carry
            result[i + 1] = total % 2
            carry = total // 2

        result[0] = carry

        # Убираем ведущий ноль если есть
        while len(result) > 1 and result[0] == 0:
            result.pop(0)

        return result

    def _binary_to_decimal(self, binary_list):
        """
        Вспомогательный метод для перевода двоичного списка в десятичное число
        """
        result = 0
        for bit in binary_list:
            result = result * 2 + bit
        return result

    # ========== НАСТОЯЩЕЕ ДВОИЧНОЕ ДЕЛЕНИЕ ==========

    def divide_in_direct_code(self, dividend, divisor, precision=5):
        """
        Деление чисел в прямом коде (НАСТОЯЩЕЕ ДВОИЧНОЕ ДЕЛЕНИЕ)
        Используется алгоритм деления столбиком в двоичной системе
        """
        if divisor == 0:
            raise ValueError(" Деление на ноль невозможно")

        # Определяем знак результата
        dividend_sign = 1 if dividend < 0 else 0
        divisor_sign = 1 if divisor < 0 else 0
        result_sign = dividend_sign ^ divisor_sign

        # Берем модули чисел
        dividend_abs = abs(dividend)
        divisor_abs = abs(divisor)

        # Получаем двоичные представления
        dividend_binary = self.converter.integer_to_binary_array(dividend_abs)
        divisor_binary = self.converter.integer_to_binary_array(divisor_abs)

        print(f"\n Двоичное представление:")
        print(f"  Делимое ({dividend_abs}) = {dividend_binary}")
        print(f"  Делитель ({divisor_abs}) = {divisor_binary}")

        # ДВОИЧНОЕ ДЕЛЕНИЕ СТОЛБИКОМ
        print(f"\n Процесс деления в двоичной системе:")
        print(f"{'=' * 60}")

        # Подготовка к делению
        quotient_binary = []  # частное
        remainder = 0
        current_value = 0

        # Деление целой части
        print(f"\n🔹 ЦЕЛАЯ ЧАСТЬ:")
        for i, bit in enumerate(dividend_binary):
            # Добавляем текущий бит к остатку (сдвиг влево и добавление бита)
            current_value = (current_value << 1) | bit

            print(f"\n  Шаг {i + 1}: Берем бит {bit}")
            print(f"    Текущее число: {self._to_binary_with_prefix(current_value)} = {current_value}")

            # Проверяем, можем ли вычесть делитель
            if current_value >= divisor_abs:
                # Вычитаем делитель
                current_value -= divisor_abs
                quotient_binary.append(1)
                print(f"     {current_value + divisor_abs} ≥ {divisor_abs} → ставим 1, остаток {current_value}")
            else:
                quotient_binary.append(0)
                print(f"     {current_value} < {divisor_abs} → ставим 0")

        # Убираем ведущие нули в частном
        while len(quotient_binary) > 1 and quotient_binary[0] == 0:
            quotient_binary.pop(0)

        # Если частное пустое, ставим 0
        if not quotient_binary:
            quotient_binary = [0]

        # Теперь обрабатываем дробную часть с заданной точностью
        print(f"\n🔹 ДРОБНАЯ ЧАСТЬ (точность {precision} знаков):")

        fractional_binary = []
        fractional_value = 0.0
        fractional_divisor = 1.0

        for i in range(precision * 4):  # Умножаем на 4 для достаточной точности
            if current_value == 0:
                break

            # Умножаем остаток на 2
            current_value *= 2
            fractional_divisor *= 2

            print(f"\n  Шаг {i + 1}: остаток × 2 = {current_value}")

            if current_value >= divisor_abs:
                current_value -= divisor_abs
                fractional_binary.append(1)
                fractional_value += 1.0 / fractional_divisor
                print(f"     {current_value + divisor_abs} ≥ {divisor_abs} → ставим 1, новый остаток {current_value}")
            else:
                fractional_binary.append(0)
                print(f"     {current_value} < {divisor_abs} → ставим 0")

            if len(fractional_binary) >= precision * 4:
                break

        # Переводим в десятичное для проверки
        integer_value = self._binary_to_decimal(quotient_binary)

        # Вычисляем дробную часть в десятичной
        fractional_decimal = 0.0
        for i, bit in enumerate(fractional_binary):
            if bit == 1:
                fractional_decimal += 2 ** (-(i + 1))

        result_abs = integer_value + fractional_decimal

        # Округляем до заданной точности
        result_abs = round(result_abs, precision)

        # Применяем знак
        if result_sign == 1:
            result_abs = -result_abs

        print(f"\n Результат деления:")
        print(f"  Целая часть в двоичной:  {quotient_binary} = {integer_value}")
        print(f"  Дробная часть в двоичной: {fractional_binary}")
        print(f"  Дробная часть в десятичной: {fractional_decimal:.{precision}f}")
        print(f"  Полный результат: {result_abs:.{precision}f}")

        return {
            'dividend': dividend,
            'divisor': divisor,
            'result_decimal': result_abs,
            'integer_binary': quotient_binary,
            'fractional_binary': fractional_binary
        }

    def _to_binary_with_prefix(self, num):
        """Вспомогательный метод для форматированного вывода двоичного числа"""
        if num == 0:
            return "[0]"
        binary = []
        n = num
        while n > 0:
            binary.insert(0, n % 2)
            n //= 2
        return str(binary)