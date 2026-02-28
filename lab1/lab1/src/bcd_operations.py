"""
Операции с двоично-десятичным кодом 8421 BCD
"""

from src.binary_processor import BinaryProcessor
from src.utils import NumberConverter


class BCD8421Converter:
    """
    Конвертер для двоично-десятичного кода 8421
    """

    # Константы для BCD
    BITS_PER_DIGIT = 4
    MAX_DIGITS = 8  # 32 бита / 4 бита на цифру

    def __init__(self, processor):
        """
        Инициализация конвертера

        Args:
            processor: экземпляр BinaryProcessor
        """
        self.processor = processor
        self.converter = NumberConverter()

    def decimal_to_bcd(self, decimal_number):
        """
        Преобразование десятичного числа в BCD 8421 код

        Args:
            decimal_number: десятичное число (неотрицательное)

        Returns:
            массив из 32 бит в BCD формате

        Raises:
            ValueError: если число отрицательное или слишком большое
        """
        if decimal_number < 0:
            raise ValueError("BCD не поддерживает отрицательные числа")

        decimal_string = str(decimal_number)
        if len(decimal_string) > self.MAX_DIGITS:
            raise ValueError(f"Слишком много цифр для 32-битного BCD")

        result = self.processor.create_zero_array()

        # Заполняем с МЛАДШЕГО разряда (справа налево)
        for digit_index, digit_char in enumerate(reversed(decimal_string)):
            digit = int(digit_char)
            self._set_bcd_digit(result, digit_index, digit)

        return result

    def bcd_to_decimal(self, bcd_array):
        """
        Преобразование BCD кода в десятичное число

        Args:
            bcd_array: массив битов BCD

        Returns:
            десятичное число
        """
        self.processor.utils.validate_binary_array(bcd_array)

        result = 0
        multiplier = 1

        # Читаем с МЛАДШЕГО разряда (справа налево)
        for position in range(self.MAX_DIGITS):
            digit_value = self._get_bcd_digit(bcd_array, position)

            # Проверка на корректность BCD цифры
            if digit_value > 9:
                break

            result += digit_value * multiplier
            multiplier *= 10

        return result

    def _get_bcd_digit(self, bcd_array, position):
        """
        Извлечение BCD цифры по позиции (0 - младшая)

        Args:
            bcd_array: массив BCD
            position: позиция цифры (0 - младшая)

        Returns:
            значение цифры
        """
        # Младшая цифра хранится в конце массива
        start = self.processor.BIT_COUNT - (position + 1) * self.BITS_PER_DIGIT
        value = 0

        for offset in range(self.BITS_PER_DIGIT):
            value = value * 2 + bcd_array[start + offset]

        return value

    def _set_bcd_digit(self, bcd_array, position, digit_value):
        """
        Установка BCD цифры (0 - младшая)

        Args:
            bcd_array: массив BCD
            position: позиция цифры (0 - младшая)
            digit_value: значение цифры (0-9)
        """
        if digit_value < 0 or digit_value > 9:
            raise ValueError(f"Некорректная BCD цифра: {digit_value}")

        # Младшая цифра записывается в конец массива
        start = self.processor.BIT_COUNT - (position + 1) * self.BITS_PER_DIGIT
        digit_binary = self.converter.integer_to_binary_array(digit_value)

        # Дополняем до 4 бит
        digit_binary = [0] * (self.BITS_PER_DIGIT - len(digit_binary)) + digit_binary

        for offset in range(self.BITS_PER_DIGIT):
            bcd_array[start + offset] = digit_binary[offset]


class BCDArithmetic:
    """
    Арифметические операции с BCD числами
    """

    def __init__(self, processor, bcd_converter):
        """
        Инициализация арифметики

        Args:
            processor: экземпляр BinaryProcessor
            bcd_converter: экземпляр BCD8421Converter
        """
        self.processor = processor
        self.bcd_converter = bcd_converter or BCD8421Converter(processor)

    def add(self, first_number, second_number):
        """
        Сложение двух чисел в BCD 8421 коде

        Args:
            first_number: первое слагаемое
            second_number: второе слагаемое

        Returns:
            словарь с результатами
        """
        first_bcd = self.bcd_converter.decimal_to_bcd(first_number)
        second_bcd = self.bcd_converter.decimal_to_bcd(second_number)

        result_bcd = self.processor.create_zero_array()
        carry = 0

        for position in range(BCD8421Converter.MAX_DIGITS):
            first_digit = self.bcd_converter._get_bcd_digit(first_bcd, position)
            second_digit = self.bcd_converter._get_bcd_digit(second_bcd, position)

            digit_sum = first_digit + second_digit + carry

            # BCD коррекция
            if digit_sum > 9:
                digit_sum += 6

            carry = digit_sum // 16  # В BCD перенос происходит при сумме >= 16
            digit_sum %= 16

            # После коррекции может потребоваться вторая коррекция
            if digit_sum > 9:
                digit_sum += 6
                digit_sum %= 16

            self.bcd_converter._set_bcd_digit(result_bcd, position, digit_sum)

        result_decimal = self.bcd_converter.bcd_to_decimal(result_bcd)

        return {
            'first': first_number,
            'second': second_number,
            'result_decimal': result_decimal,
            'first_binary': first_bcd,
            'second_binary': second_bcd,
            'result_binary': result_bcd
        }